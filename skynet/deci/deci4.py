#!/usr/bin/env python

import array
import getpass
import select
import socket
import struct
import sys
import threading
import time
import traceback

if sys.version_info[0] < 3:
    raise Exception("Python 3 required")

log_level = 0

def log(*args):
    if log_level >= 2:
        log_string = ''
        for arg in args:
            log_string += str(arg)
        if (len(log_string)):
            print( log_string )
    return

def make_dump(bytes):
    """ print a byte array as a memory dump, 16 bytes per line, both as hex and ASCII """

    def chunker(l,n):
        """ chop iterable l into n length pieces """
        for i in range(0,len(l),n):
            yield l[i:i+n]

    def makewords(l):
        """ Return list of bytes as hex strings in 2 byte blocks as string 
            i.e.   1234 5678 9ABC DEF0 """

        for i in range(0,len(l),2):
            s = l[i][2:]

            if i+1 < len(l):
                s += l[i+1][2:].zfill(2)

            yield s.zfill(4)

    def ascdisp(b):
        """ return as ASCII, using '.' for control codes """
        x = int(b,16)
        
        if x < 32 or x > 127:
            return '.'
        else:
            return chr(x)
             

    if type(bytes) is str:
        bytes = [ord(x) for x in bytes]

    rc = ""
    for addr, line in enumerate(chunker(list(map(hex, bytes)), 16)):
        rc += "%6s: %-39s %s\n" % (hex(addr * 16),
                                  ' '.join(makewords(line)),
                                  ''.join(map(ascdisp,line)))
    return rc


def summarize(buffer):
    protocol = struct.unpack_from("<L", buffer, 8)[0]
    msgtype = struct.unpack_from("<L", buffer, 16)[0]

    protcls = None
    for cls in [NetmpProt, TsmpProt, TtypProt, CtrlpProt]:
        if cls.PROTOCOL == protocol:
            protcls = cls
            break

    if protcls:
        protocolname = protcls.__name__[:-4]
    else:
        protocolname = hex(protocol)

    msgtypename = None
    for fld in dir(protcls):
        trgt = "SCE_" + protocolname.upper() + "_TYPE_"
        if fld.startswith(trgt):
            if getattr(cls, fld) == msgtype:
                msgtypename = fld[len(trgt):]

    if not msgtypename:
        msgtypename = hex(msgtype)

    return "%s:%s" % (protocolname, msgtypename)


# Basic description of the protocol
#
# DECI contains multiple sub-protocols which are very similar to each other.  Each protocol is intended to be used
# with a different socket connection.  This is to allow the client to easily keep messages for each protocol 
# separate.
#
# The primary protocol is "NETMP".  This is used to control initiation of all other protocols.  In order to use DECI,
# you connect to the device using a socket connection to port 8550.  The docs call this "stream 1".  In order
# to access other protocols, you must "register" them with NETMP.  You do this by sending a REGISTER command with
# the appropriate protocol id for the one you wish to register.  You then must talk to the devkit with this 
# protocol on an entirely new socket connection.  So, to start using CTRLP, you must do the following:
#
# * Create a socket connection to port 8550 of the devkit
# * Send a SCE_NETMP_TYPE_CONNECT_CMD message on that socket
# * Receive the SCE_NETMP_TYPE_CONNECT_RES response on that socket.  This will contain the "netmp key"
# * Create a second socket connection to port 8550 of the devkit
# * Send a SCE_NETMP_TYPE_REGISTER_CMD message with the netmp key and the CTRLP protocol id (0x0002c000) on the new socket
# * Receive the SCE_NETMP_TYPE_REGISTER_RES response on that socket.
# * Use CTRLP by sending CTRLP messages on the second socket connection
# 
# When the script ends, it should send an "UNREGISTER" message to NETMP using the appropriate protocol key on the
# NETMP socket connection.  It should then send a disconnect message through NETMP
#
# When a "CONNECT" message is sent through NETMP, any connections through target manager will be disconnected.
class Deci4HProt:
    """ Common base class for protocol classes.  Not intended to be instatiated.  Used to contain common code.  """

    @staticmethod
    def pad_len(length, multiple):
        """ Return first multiple above length """

        if (length // multiple) * multiple != length:
            return ((length // multiple) + 1 ) * multiple
        return length

    class PlayException(Exception):
        def __init__(self, length):
            self.length = length

        def __str__(self):
            return "You set the length to %d but the max is 8.  This will cause the playback system to bork, and you'll need to reboot, so don't do that" % self.length

    recorddefs = {
        "SceDeciHeader": [
            {"type":'B', "length":1, "name":"version"},
            {"type":"zeros", "length":3},
            {"type":'<l', "length":4, "name":"length"},
            {"type":'<L', "length":4, "name":"protocol"}
        ],
        "SceDeciUlpCmdHdr":[
            {"type":'<H', "length":2, "name":"seqnumber"},
            {"type":'<H', "length":2, "name":"fraginfo"},
            {"type":'<l', "length":4, "name":"msgtype"}

        ],
        "SceDeciUlpNtfHdr":[
            {"type":'<H', "length":2, "name":"seqnumber"},
            {"type":'<H', "length":2, "name":"fraginfo"},
            {"type":'<l', "length":4, "name":"msgtype"},
            {"type":'<Q', "length":8, "name":"timestamp"}
        ],
        "SceDeciUlpResHdr":[
            {"type":'<H', "length":2, "name":"seqnumber"},
            {"type":'<H', "length":2, "name":"fraginfo"},
            {"type":'<l', "length":4, "name":"msgtype"},
            {"type":'<l', "length":4, "name":"result"},
            {"type":'<l', "length":4, "name":"aux_error_code"}
        ],
        "SceDeciCommonConfig":[
            {"type":'<l', "length":4, "name":"payload_length"},
            {"type":'<l', "length":4, "name":"feature_number"},
            {"type":'<l', "length":4, "name":"min_feature_number"},
            {"type":'<l', "length":4, "name":"max_size_to_host"},
            {"type":'<l', "length":4, "name":"max_size_to_target"},
            {"type":'<l', "length":4, "name":"flags"}
        ],
        "SceNetmpConnectCmd":[
            {"type":"SceDeciStringUtf8", "name":"client_id"},
            {"type":"zeros", "length":4},
            {"type":'<H', "length":2, "name":"udpport"},
            {"type":"zeros", "length":2}
        ],
        "SceNetmpConnectRes":[
            {"type":'<L', "length":4, "name":"netmp_key"},
        ],
        "SceNetmpRegisterCmd":[
            {"type":'<L', "length":4, "name":"netmp_key"},
            {"type":'<L', "length":4, "name":"reg_protocol"}
        ],
        "SceNetmpUnregisterCmd":[
            {"type":'<L', "length":4, "name":"reg_protocol"}
        ],
        "SceNetmpRegInfo": [
            {"type":'<L', "length":4, "name":"size"},
            {"type":'<L', "length":4, "name":"protocol"},
            {"type":'<L', "length":4, "name":"timestamp"},
            {"type":"SceDeciStringUtf8", "name":"owner"}
        ],
        "SceGetConfCmd":[
            {"type":'<l', "length":4, "name":"in_buf_size"}
        ],
        "SceCtrlpDevices":[
            {"type":'<L', "length":4, "name":"controller"}  # actually bitfield
        ],
        "SceCtrlpPlayCmd": [
            {"type":'<l', "length":4, "name":"threshold"}
        ],
        "SceCtrlpData":[
            {"type":'<L', "length":4, "name":"size"},
            {"type":'<Q', "length":8, "name":"timestamp"},
            {"type":'<L', "length":4, "name":"unionsize"},
            {"type":'<L', "length":4, "name":"datatype"},
            {"type":'<L', "length":4, "name":"datasize"},
            {"type":'<L', "length":4, "name":"controller"},
            {"type":'<L', "length":4, "name":"buttons"},
            {"type":'<B', "length":1, "name":"lx"},
            {"type":'<B', "length":1, "name":"ly"},
            {"type":'<B', "length":1, "name":"rx"},
            {"type":'<B', "length":1, "name":"ry"},
            {"type":'<B', "length":1, "name":"l2"},
            {"type":'<B', "length":1, "name":"r2"},
            {"type":"zeros", "length":2},
            {"type":'<L', "length":4, "name":"touchsize"},
            {"type":'<Q', "length":8, "name":"timestamp2"},

            {"type":"zeros", "length":4}  # list term, assume zero for now  (no list)
        ],
        "SceCtrlpPlayDataRes":[
            {"type":'<L', "length":4, "name":"count"}  # number of entries left in buffer?
        ],
        "SceTtypOut": [
            {"type":'<L', "length":4, "name":"port"},
            {"type":'<L', "length":4, "name":"category"},
            {"type":'<L', "length":4, "name":"pid"},
            {"type":'<L', "length":4, "name":"tid"},
            {"type":'SceDeciTtyStreamData', "name":"message"}
        ],
        "SceTtypPortState": [
            {"type":'<L', "length":4, "name":"size"},
            {"type":'<L', "length":4, "name":"port"},
            {"type":'<L', "length":4, "name":"mask"},
            {"type":'<L', "length":4, "name":"state"}
        ],
        "SceTsmpNameValueDisplay": [
            {"type":'<L', "length":4, "name":"size"},
            {"type":"SceDeciStringUtf8", "name":"name"},
            {"type":"SceDeciVariant", "name":"value"},
            {"type":'<L', "length":4, "name":"format"},
        ],
        "SceTsmpPowerRequest": [
            {"type":'<L', "length":4, "name":"powerstate"},
        ],
        "SceTsmpGetPsnStateCmd": [
            {"type":"SceDeciStringUtf8", "name":"username"},  # actually SceDeciStringAscii
        ],
        "SceTsmpGetPsnStateRes": [
            {"type":'<L', "length":4, "name":"psnState"},
        ],
        "SceTsmpPowerState": [
            {"type":'<L', "length":4, "name":"powerState"},
        ],
        "SceTsmpGetPict": [
            {"type":'<L', "length":4, "name":"mode"},
        ]
    }
    sequence = 0x1234

    def build_buffer(self, format, **kwargs):
        """ Format bytes according to the passed in format, using kwargs as values """

        # formats
        #
        # SceDeciStringUtf8 - string begining with 32 bit length
        # zeros - padding.  Ignored
        # All others are python struct formats
        for f in format:
            if f["type"] == "SceDeciStringUtf8":
                f["length"] = self.pad_len(len(kwargs[f["name"]]),4) + 4
                #f["length"] = len(kwargs[f["name"]]) + 4

        length = sum(f["length"] for f in format) 
        buffer = array.array('B', [0]*length)

        offset = 0
        for f in format:
            if f["type"] != "zeros":
                if f["name"] == "length":
                    val = length
                else:
                    val = kwargs[f["name"]]

                if f["type"] != "SceDeciStringUtf8":
                    struct.pack_into(f["type"], buffer, offset, val)
                else:
                    struct.pack_into("<l", buffer, offset, len(val))
                    struct.pack_into("%ds" % len(val), buffer, offset+4, val.encode("utf8"))


            offset += f["length"]

        return buffer

    def set_length(sef, buffer, format, length):
        """ write the length bytes as specified in the length field in the format """
        offset = 0
        for f in format:
            if f["type"] != "zeros":
                if f["name"] == "length":
                    struct.pack_into(f["type"], buffer, offset, length)

            offset = offset + f["length"]
        
    def parse_buffer(self, buffer, format, res):
        """ Read a byte array and return a set of key/valye pairs

            buffer - byte array input
            format - list of formats to apply to buffer
            res - key/value pairs from previous parses
                  new values inserted into this
                
            returns:
                buffer

        """

        tmpbuff = buffer
        offset = 0
        for f in format:
            if f["type"] == "SceDeciTtyStreamData":
                length = struct.unpack_from("<L", buffer, offset)[0]
                offset += 4
                res[f["name"]] = struct.unpack_from("<%ds" % length, buffer, offset)[0].decode("utf-8")
                offset += self.pad_len(length, 4)

            elif f["type"] == "SceDeciStringUtf8":
                length = struct.unpack_from("<L", buffer, offset)[0]
                offset += 4

                # Ignore null terminator
                if length > 0:
                    res[f["name"]] = struct.unpack_from("<%ds" % (length-1), buffer, offset)[0].decode("utf-8")
                else:
                    res[f["name"]] = ""

                offset += self.pad_len(length,4)

            elif f["type"] == "SceDeciVariant":
                size = struct.unpack_from("<L", buffer, offset)[0]
                type = struct.unpack_from("<L", buffer, offset+4)[0]

                if type == 0:
                    res[f["name"]] = struct.unpack_from("<L", buffer, offset+8)[0]
                elif type == 1:
                    res[f["name"]] = struct.unpack_from("<l", buffer, offset+8)[0]
                if type == 2:
                    res[f["name"]] = struct.unpack_from("<Q", buffer, offset+8)[0]
                elif type == 3:
                    res[f["name"]] = struct.unpack_from("<q", buffer, offset+8)[0]
                elif type == 4 or type == 5:
                    pass # ignore 128 bit for now
                elif type == 7:
                    length = struct.unpack_from("<L", buffer, offset+8)[0]
                    res[f["name"]] = struct.unpack_from("<%ds" % (length-1), buffer, offset+12)[0].decode("utf-8")
                elif type == 8:
                    length = struct.unpack_from("<L", buffer, offset+8)[0]
                    res[f["name"]] = struct.unpack_from("<%ds" % length, buffer, offset+12)[0]

                offset += size

            else:
                if f["type"] != "zeros":
                    res[f["name"]] = struct.unpack_from(f["type"], buffer, offset)[0]

                offset += f["length"]

        return buffer[offset:]

    def make_deci_cmd_header(self, inbuff, message, protocol):
        """ put a standard deci cmd header in front of the message in inbuff 
        
        
            inbuff - A Deci message with no header as bytes
            message - The message id of the message
            protocol - the protocol of the message
        """

        buffer = self.build_buffer(Deci4HProt.recorddefs["SceDeciHeader"], version=0x41, protocol=protocol)
        buffer.extend(self.build_buffer(Deci4HProt.recorddefs["SceDeciUlpCmdHdr"], seqnumber=Deci4HProt.sequence, fraginfo=0, msgtype=message))
        Deci4HProt.sequence += 1

        if inbuff:
            buffer.extend(inbuff)

        self.set_length(buffer, Deci4HProt.recorddefs["SceDeciHeader"], len(buffer))

        return buffer

    def parse_header(self, buffer):
        """ Read the standard response headers from a byte array 

            buffer - byte array representing the entire message

            returns:

                buffer - A byte array with the headers stripped off
                res - A set of key/value pairs representing data pulled from headers.

                important ones include:

                    version - deci version.  (Must be 0x41 or we likely break)
                    length - length of the entire message including header
                    protocol - The protocol id
                    seqnumber - Sequence number that matches value passed in CMD message
                    msgtype - The message id
        """

        res = {}
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciHeader"], res)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciUlpResHdr"], res)

        return buffer, res



class DeciQueue:
    def __init__(self, ip, port):
        self._stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stream.connect((ip, port))

        self._responses = {}
        self._notifications = {}
        self._conditions = {}

        self._tosend = []
        self._run = True
        self._sendlock = threading.Lock()
        self._recvlock = threading.Lock()

        self._rwthread = threading.Thread(name="DeciQueue",
                                          target=self._readwrite,
                                          args=(self, 'dummy'))

        self._rwthread.start()
        self._workbuff = None
        self._worklength = None
        self._notifications = [] # may need to purge this periodically

    def _readwrite(self, *args, **kwargs):

        if log_level > 0:
            print("Start thread for %d - %s" % (self._stream.fileno(), self) )
        while self._run:
            respondevent = []

            rd,wr,ex = select.select([self._stream], [self._stream], [], 0)

            if self._stream in rd:
                # To read a full message, we have to read 8 bytes to determin length, then
                # read the rest of the bytes until we reach length.  At any time in this
                # process, the current read could end.  We build the message in _workbuff
                # over potentionally multiple passes, with _worklength set once we've read 8
                if self._recvlock.acquire(blocking=False):

                    # Reading the length (first read, or we haven't gotten 8 bytes yet)
                    if not self._workbuff or not self._worklength:
                        if not self._workbuff:
                            self._workbuff = self._stream.recv(8)
                        elif not self._worklength:
                            self._workbuff += self._stream.recv(8-len(self._workbuff))
                            
                        if len(self._workbuff) >= 8:
                            self._worklength = struct.unpack_from("<L", self._workbuff, 4)[0]

                    # reading the rest of the message
                    else:
                        self._workbuff += self._stream.recv(self._worklength-len(self._workbuff))
                        if len(self._workbuff) == self._worklength:

                            result = struct.unpack_from("<L", self._workbuff, 20)[0]
                            if log_level >= 1:
                                print("RECV %d - %s (%s)" % (self._stream.fileno(),summarize(self._workbuff), hex(result)))
                            log( "RECV (%s):\n%s" % (self._stream, make_dump(self._workbuff)) )

                            sequence = struct.unpack_from("<H", self._workbuff, 12)[0]

                            #hack!
                            protocol = struct.unpack_from("<L", self._workbuff, 8)[0]
                            msgtype = struct.unpack_from("<L", self._workbuff, 16)[0]
                            if msgtype >= 0x80 or (msgtype == 0x7 and protocol == CtrlpProt.PROTOCOL):
                                self._notifications.append(self._workbuff)
                            else:
                                if sequence not in self._responses:
                                    self._responses[sequence] = []
                                self._responses[sequence].append(self._workbuff)
                                respondevent.append(sequence)


                            self._workbuff = None
                            self._worklength = None

                    self._recvlock.release()

            # must happen here to avoid race condition with _recvlock
            for sequence in respondevent:
                if sequence in self._conditions:
                    condition = self._conditions[sequence]
                    condition.acquire()
                    condition.notify()
                    condition.release()

            if self._stream in wr:
                if self._sendlock.acquire(blocking=False):
                    if len(self._tosend) > 0:
                        if log_level >= 1:
                            print("SEND %d - %s" % (self._stream.fileno(),summarize(self._tosend[0])))
                        log( "SEND (%s):\n%s" % (self._stream, make_dump(self._tosend[0])) )
                        self._stream.send(self._tosend[0])
                        #if success:
                        self._tosend.pop(0)

                    self._sendlock.release()


    def stop(self):
        self._run = False
        self._rwthread.join()

        try:
            self._stream.shutdown(socket.SHUT_RDWR)
            pass
        except OSError:
            # the socket may already be in shutdown state when the last protocol was closed,
            # so ignore the exception that would then be thrown by shutdown()
            pass
        finally:
            self._stream.close()

    def send(self, buffer, condition=None):
        with self._sendlock:
            sequence = struct.unpack_from("<H", buffer, 12)[0]
            
            self._tosend.append(buffer)

        if condition:
            self._conditions[sequence] = condition

        return sequence 

    def recv(self,sequence):
        with self._recvlock:
            if sequence in self._responses:
                # todo not sure why this needed, Y YU HAV NO DATA!?
                if len(self._responses[sequence]) > 0:
                    buffer = self._responses[sequence].pop(0)

                    fraginfo = struct.unpack_from("<H", buffer, 14)[0]
                    fragcontinue = (fraginfo & 0x8000 != 0)

                    if not fragcontinue:
                        del self._responses[sequence]

                    return buffer

            return None

    def sendrecvmult(self, buffer):
        condition = threading.Condition()
        sequence = self.send(buffer, condition)
        self._responses[sequence] = []

        lastfrag = -1
        fragcontinue = True
        fragearly = False
        while fragcontinue and not fragearly:
            condition.acquire()
            condition.wait()
            condition.release()

            while True:
                buffer = self.recv(sequence)
                if not buffer:
                    break

                fraginfo = struct.unpack_from("<H", buffer, 14)[0]
                fragcontinue = (fraginfo & 0x8000 != 0)
                fragearly = (fraginfo & 0x4000 != 0)
                fragval = fraginfo & 0x3FFF

                yield buffer

        with self._recvlock:
            if sequence in self._conditions:
                del self._conditions[sequence]

    def sendrecv(self, buffer):
        #todo: rework.  Should we paste allmultipart messages together?
        l = [b for b in self.sendrecvmult(buffer)]
        if len(l) != 1:
            raise "Multipart message not expected"
            
        return l[0]

    def get_notification(self):
        with self._recvlock:
            if len(self._notifications) > 0:
                return self._notifications.pop(0)
            return None

# Basic organization
# 
# Each protocol has two classes:
#
# FooProt - Derived from Deci4HProt, responsible for generating messages and parsing responses.
# Foo - Derived from DeciQueue; ties a stream to a protocol and presents method interface to caller
#
# FooProt organization:
# Set of constants in form SCE_*_TYPE_* representing message ids
# Constant for protocol id
# methods for each message type:
# *_cmd method - returns a buffer formated as a message, takes values to apply as arguments
# *_parse method - Takes a buffer and parses the values into a key/value set

class NetmpProt(Deci4HProt):
    SCE_NETMP_TYPE_GET_CONF_CMD = 0x0
    SCE_NETMP_TYPE_GET_CONF_RES = 0x1
    SCE_NETMP_TYPE_CONNECT_CMD = 0x2
    SCE_NETMP_TYPE_CONNECT_RES = 0x3
    SCE_NETMP_TYPE_DISCONNECT_CMD = 0x4
    SCE_NETMP_TYPE_DISCONNECT_RES = 0x5
    SCE_NETMP_TYPE_REGISTER_CMD = 0x6
    SCE_NETMP_TYPE_REGISTER_RES = 0x7
    SCE_NETMP_TYPE_UNREGISTER_CMD = 0x8
    SCE_NETMP_TYPE_UNREGISTER_RES = 0x9
    SCE_NETMP_TYPE_FORCE_DISCONNECT_CMD = 0xa
    SCE_NETMP_TYPE_FORCE_DISCONNECT_RES = 0xb
    SCE_NETMP_TYPE_GET_REGISTERED_LIST_CMD = 0xe
    SCE_NETMP_TYPE_GET_REGISTERED_LIST_RES = 0xf
    #SCE_NETMP_TYPE_FORCE_DISCON_NOTIFICATION = 0x41
    SCE_NETMP_TYPE_INVALPROTO_NOTIFICATION = 0xe2
    PROTOCOL = 0x40001000

    SCE_DECI_NETMP_ERROR_INUSE = 0x1006

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciCommonConfig"], res)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceGetConfCmd"], res)
        return buffer, res

    def connect_cmd(self, client_id, udpport):

        buffer = self.build_buffer(Deci4HProt.recorddefs["SceNetmpConnectCmd"], client_id=client_id, udpport=udpport)
        buffer = self.make_deci_cmd_header(buffer, self.SCE_NETMP_TYPE_CONNECT_CMD, self.PROTOCOL)

        return buffer

    def connect_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceNetmpConnectRes"], res)

        return buffer, res

    def disconnect_cmd(self):

        buffer = self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_DISCONNECT_CMD, self.PROTOCOL)

        return buffer

    def disconnect_parse(self, buffer):
        buffer, res = self.parse_header(buffer)

        return buffer, res

    def force_disconnect_cmd(self):

        buffer = self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_FORCE_DISCONNECT_CMD, self.PROTOCOL)

        return buffer

    def force_disconnect_parse(self, buffer):
        buffer, res = self.parse_header(buffer)

        return buffer, res


    def register_cmd(self, netmp_key, reg_protocol):

        buffer = self.build_buffer(Deci4HProt.recorddefs["SceNetmpRegisterCmd"], netmp_key=netmp_key, reg_protocol=reg_protocol)
        buffer = self.make_deci_cmd_header(buffer, self.SCE_NETMP_TYPE_REGISTER_CMD, self.PROTOCOL)

        return buffer

    def register_parse(self, buffer):
        buffer, res = self.parse_header(buffer)

        return buffer, res

    def unregister_cmd(self, reg_protocol):

        buffer = self.build_buffer(Deci4HProt.recorddefs["SceNetmpUnregisterCmd"], reg_protocol=reg_protocol)
        buffer = self.make_deci_cmd_header(buffer, self.SCE_NETMP_TYPE_UNREGISTER_CMD, self.PROTOCOL)

        return buffer

    def unregister_parse(self, buffer):
        buffer, res = self.parse_header(buffer)

        return buffer, res

    def get_registered_list_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_GET_REGISTERED_LIST_CMD, self.PROTOCOL)

 #   def get_registered_list_msg(self, stream):
 #       buffer = self.sendrecv(stream, self.get_registered_list_cmd())
 #       buffer, res = self.parse_header(buffer)
 #       res["data"] = []
 #       terminator = struct.unpack_from("<l", buffer, 0)[0]
 #       while(terminator > 0):
 #           resdata = {}
 #           buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceNetmpRegInfo"], resdata)
 #           res["data"].append(resdata)
 #           terminator = struct.unpack_from("<l", buffer, 0)[0]

        return res


class CtrlpProt(Deci4HProt):
    SCE_CTRLP_TYPE_GET_CONF_CMD = 0x0
    SCE_CTRLP_TYPE_GET_CONF_RES = 0x1
    SCE_CTRLP_TYPE_REC_START_CMD = 0x2
    SCE_CTRLP_TYPE_REC_START_RES = 0x3
    SCE_CTRLP_TYPE_REC_STOP_CMD = 0x4
    SCE_CTRLP_TYPE_REC_STOP_RES = 0x5
    SCE_CTRLP_TYPE_REC_DATA_NOTIFICATION = 0x7
    SCE_CTRLP_TYPE_PLAY_START_CMD = 0x8
    SCE_CTRLP_TYPE_PLAY_START_RES = 0x9
    SCE_CTRLP_TYPE_PLAY_STOP_CMD = 0xA
    SCE_CTRLP_TYPE_PLAY_STOP_RES = 0xB
    SCE_CTRLP_TYPE_PLAY_DATA_CMD = 0xC
    SCE_CTRLP_TYPE_PLAY_DATA_RES = 0xD
    PROTOCOL = 0x0002c000

    class OutOfMemoryException(Exception):
        
        def __str__(self):
            return "Out of playback buffer space on remote"

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_CTRLP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciCommonConfig"], res)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceGetConfCmd"], res)
        return buffer, res

    def rec_start_cmd(self, controller=0xffffffff):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceCtrlpDevices"], controller=controller)
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_REC_START_CMD, self.PROTOCOL)

    def rec_start_parse(self, buffer):
        return self.parse_header(buffer)
        
    def rec_stop_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_CTRLP_TYPE_REC_STOP_CMD, self.PROTOCOL)

    def rec_stop_parse(self, buffer):
        return self.parse_header(buffer)

    def play_start_cmd(self, controller=0xffffffff):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceCtrlpDevices"], controller=controller)
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_START_CMD, self.PROTOCOL)

    def play_start_parse(self, buffer):
        return self.parse_header(buffer)

    def play_data_cmd(self, events):
        if len(events) > 8:
            raise self.PlayException(len(events))

        buffer = self.build_buffer(Deci4HProt.recorddefs["SceCtrlpPlayCmd"], threshold=0)

        for button in events:
            buffer.extend(self.build_buffer(Deci4HProt.recorddefs["SceCtrlpData"], 
                size = 56,
                timestamp = 0,
                unionsize = 44,
                datatype = 0,
                datasize = 36,
                controller = 0,
                buttons = button,
                lx = 128,
                ly = 128,
                rx = 128,
                ry = 128,
                l2 = 0,
                r2 = 0,
                touchsize = 12,
                timestamp2 = 0))
            
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_DATA_CMD, self.PROTOCOL)


    def play_data_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceCtrlpPlayDataRes"], res)
        return buffer, res

    def play_raw_data_cmd(self, block):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceCtrlpPlayCmd"], threshold=0)
        buffer += block
        buffer = self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_DATA_CMD, self.PROTOCOL)
        return buffer

    def play_raw_data_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceCtrlpPlayDataRes"], res)
        return buffer, res

    def play_stop_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_CTRLP_TYPE_PLAY_STOP_CMD, self.PROTOCOL)

    def play_stop_parse(self, buffer):
        return self.parse_header(buffer)

    def notification_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        if res['msgtype'] == CtrlpProt.SCE_CTRLP_TYPE_REC_DATA_NOTIFICATION:
            pass

        return buffer, res

class TtypProt(Deci4HProt):
    """ Protocol for tty messages.  Note that merely registering this protocol will cause it to spit
        tty messages at you. """
    SCE_TTYP_TYPE_GET_CONF_CMD = 0x0
    SCE_TTYP_TYPE_GET_CONF_RES = 0x1
    SCE_TTYP_TYPE_TTY_IN_CMD = 0x2
    SCE_TTYP_TYPE_TTY_IN_RES = 0x3
    SCE_TTYP_TYPE_GET_PORT_STATES_CMD = 0x4
    SCE_TTYP_TYPE_GET_PORT_STATES_RES = 0x5
    SCE_TTYP_TYPE_SET_PORT_STATES_CMD = 0x7
    SCE_TTYP_TYPE_SET_PORT_STATES_RES = 0x8
    SCE_TTYP_TYPE_TTY_OUT_NOTIFICATION = 0x80
    SCE_TTYP_TYPE_IN_BUFF_READY_NOTIFICATION = 0x81
    SCE_TTYP_TYPE_IN_CLOSE_NOTIFICATION = 0x82
    SCE_TTYP_TYPE_FATALHEAD_NOTIFICATION = 0xE0
    SCE_TTYP_TYPE_INVALHEAD_NOTIFICATION = 0xE1
    SCE_TTYP_TYPE_INVALPROTO_NOTIFICATION = 0xE2
    PROTOCOL = 0x80003000

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TTYP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciCommonConfig"], res)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceGetConfCmd"], res)
        return buffer, res


    def get_port_states_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TTYP_TYPE_GET_PORT_STATES_CMD, self.PROTOCOL)

    def get_port_states_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        if res['msgtype'] == self.SCE_TTYP_TYPE_GET_PORT_STATES_RES:
            res["data"] = []
            elements = struct.unpack_from("<l", buffer, 0)[0]
            buffer = buffer[8:] # skip num elements and elment size

            for i in range(elements):
                resdata = {}
                buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTtypPortState"], resdata)
                res["data"].append(resdata)

        return buffer, res


    def notification_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        if res['msgtype'] == TtypProt.SCE_TTYP_TYPE_TTY_OUT_NOTIFICATION:
            buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTtypOut"], res)


        return buffer, res

class TsmpProt(Deci4HProt):
    SCE_TSMP_TYPE_GET_CONF_CMD = 0x0
    SCE_TSMP_TYPE_GET_CONF_RES = 0x1
    SCE_TSMP_TYPE_GET_INFO_CMD = 0x2
    SCE_TSMP_TYPE_GET_INFO_RES = 0x3
    SCE_TSMP_TYPE_POWER_CONTROL_CMD = 0x4
    SCE_TSMP_TYPE_POWER_CONTROL_RES = 0x5
    SCE_TSMP_TYPE_GET_POWER_STATUS_CMD = 0x6
    SCE_TSMP_TYPE_GET_POWER_STATUS_RES = 0x7
    SCE_TSMP_TYPE_GET_GET_PICT_CMD = 0x18
    SCE_TSMP_TYPE_GET_GET_PICT_RES = 0x19
    SCE_TSMP_TYPE_GET_PSN_STATE_CMD = 0x20
    SCE_TSMP_TYPE_GET_PSN_STATE_RES = 0x21
    PROTOCOL = 0x80004000

    POWER_OFF = 0x100
    POWER_REBOOT = 0x200

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceDeciCommonConfig"], res)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceGetConfCmd"], res)
        return buffer, res

    def get_info_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_INFO_CMD, self.PROTOCOL)

    def get_info_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTsmpNameValueDisplay"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return buffer, res

    def power_control_cmd(self, powerstate):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceTsmpPowerRequest"], powerstate=powerstate)
        return self.make_deci_cmd_header(buffer, self.SCE_TSMP_TYPE_POWER_CONTROL_CMD, self.PROTOCOL)

    def power_control_parse(self, buffer):
        return self.parse_header(buffer)

    def power_status_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_POWER_STATUS_CMD, self.PROTOCOL)

    def power_status_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTsmpPowerState"], res)
        return buffer, res

    def get_pict_cmd(self, mode):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceTsmpGetPict"], mode=mode)
        return self.make_deci_cmd_header(buffer, self.SCE_TSMP_TYPE_GET_GET_PICT_CMD, self.PROTOCOL)

    def get_pict_parse(self, buffer):
        return self.parse_header(buffer)

    def get_psn_state_cmd(self, username):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceTsmpGetPsnStateCmd"], username=username)
        return self.make_deci_cmd_header(buffer, self.SCE_TSMP_TYPE_GET_PSN_STATE_CMD, self.PROTOCOL)

    def get_psn_state_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTsmpGetPsnStateRes"], res)
        return buffer, res

class Netmp(DeciQueue):
    class InUseException(Exception):
        
        def __str__(self):
            return "Another system is controlling this device"

    class NetmpException(Exception):

        def __init__(self, err):
            self.err = err

        def __str__(self):
            return "Error 0x%x trying to send netmp command" % self.err

    def __init__(self, ip, port=8550):
        self.prot = NetmpProt()
        self._ip = ip
        self._port = port

        super(Netmp, self).__init__(ip, port)

        self._counts = {}
        self._registered = {}

    def _refcnt_inc(self, counter):
        if counter not in self._counts:
            self._counts[counter] = 0

        self._counts[counter] += 1

        return self._counts[counter] == 1

    def _refcnt_dec(self, counter):
        if self._counts[counter] > 0:
            self._counts[counter] -= 1

            if self._counts[counter] == 0:
                return True

        return False

    def connect(self, client_id = None):
        if not client_id:
            try:
                client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostbyname(socket.gethostname()))
            except socket.gaierror:
                client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostname())
            

        buffer = self.prot.connect_cmd(client_id=client_id, udpport=0)
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.connect_parse(buffer)

        self.netmp_key = res["netmp_key"]
        return res

    def get_conf(self):
        buffer = self.prot.get_conf_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_conf_parse(buffer)

        return res

    def register(self, cls):
        if cls not in self._registered:
            try:
                self._registered[cls] = cls(self, self._ip, self._port)
            except Netmp.InUseException:
                raise


        self._refcnt_inc(cls)

        return self._registered[cls]

    def unregister(self, cls):
        if self._refcnt_dec(cls):
            self._registered[cls].stop()

            buffer = self.prot.unregister_cmd(reg_protocol=self._registered[cls].prot.PROTOCOL)
            buffer = self.sendrecv(buffer)
            buffer, res = self.prot.unregister_parse(buffer)

            return res

    def force_disconnect(self):
        buffer = self.prot.force_disconnect_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.force_disconnect_parse(buffer)

        return res
        
    def get_registered_list(self):
        buffer = self.prot.get_registered_list_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.parse_header(buffer)
        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.prot.parse_buffer(buffer, Deci4HProt.recorddefs["SceNetmpRegInfo"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return res

    def get_owner(self):
        res = self.get_registered_list()
        for l in res["data"]:
            if (l["protocol"] & 0x80000000) == 0:
                return l["owner"]

        return None
        
    def disconnect(self):
        buffer = self.prot.disconnect_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.disconnect_parse(buffer)

        for obj in self._registered.values():
            obj.stop() 

        self.stop()

        return res

class Ctrlp(DeciQueue):
    def __init__(self, netmp, ip, port):
        self.prot = CtrlpProt()

        super(Ctrlp, self).__init__(ip, port)

        buffer = netmp.prot.register_cmd(netmp_key=netmp.netmp_key, reg_protocol=CtrlpProt.PROTOCOL)
        buffer = self.sendrecv(buffer)
        buffer, res = netmp.prot.register_parse(buffer)

        if res["result"]:
            self.stop()
            if res["result"] == NetmpProt.SCE_DECI_NETMP_ERROR_INUSE:
                raise Netmp.InUseException()
            elif res["result"]:
                raise self.NetmpException(res["result"])

    def get_conf(self):
        buffer = self.prot.get_conf_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_conf_parse(buffer)

        return res

    def rec_start(self):
        buffer = self.prot.rec_start_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.rec_start_parse(buffer)

    def rec_stop(self):
        buffer = self.prot.rec_stop_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.rec_stop_parse(buffer)

    def read_raw_data(self):
        buffer = self.get_notification()
        if buffer:
            buffer, res = self.prot.notification_parse(buffer)
            if res['msgtype'] == CtrlpProt.SCE_CTRLP_TYPE_REC_DATA_NOTIFICATION:
                return buffer
            else:
                pass # need to save these somewhere

        return None

    def play_start(self):
        buffer = self.prot.play_start_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.play_start_parse(buffer)

    def play_data(self, events):
        buffer = self.prot.play_data_cmd(events)
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.play_data_parse(buffer)
        return res

    # Not currently working.  Need to investigate
    #def play_raw_data(self, block):
    #    buffer = self.prot.play_raw_data_cmd(block)
    #    buffer = self.sendrecv(buffer)
    #    buffer, res = self.prot.play_raw_data_parse(buffer)

    def play_stop(self):
        buffer = self.prot.play_stop_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.play_stop_parse(buffer)

class Ttyp(DeciQueue):
    def __init__(self, netmp, ip, port):
        self.prot = TtypProt()

        super(Ttyp, self).__init__(ip, port)

        buffer = netmp.prot.register_cmd(netmp_key=netmp.netmp_key, reg_protocol=TtypProt.PROTOCOL)
        buffer = self.sendrecv(buffer)
        buffer, res = netmp.prot.register_parse(buffer)

        if res["result"]:
            self.stop()
            raise self.NetmpException(res["result"])

    def get_conf(self):
        buffer = self.prot.get_conf_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_conf_parse(buffer)

        return res

    def get_port_states(self):
        buffer = self.prot.get_port_states_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_port_states_parse(buffer)

        return res

    def read(self):
        """ Reads a tty message without blocking.  If no messages pending, returns None """

        buffer = self.get_notification()
        if buffer:
            buffer, res = self.prot.notification_parse(buffer)
            if res['msgtype'] == TtypProt.SCE_TTYP_TYPE_TTY_OUT_NOTIFICATION:
                return res
            else:
                pass # need to save these somewhere

        return None
                
    # todo Event?
    def readsync(self):
        res = None

        while not res:
            res = self.read()
            
        return res

         
class Tsmp(DeciQueue):
    MODE_GAME = 0
    MODE_SYSTEM = 1
    MODE_AUTO = 2

    def __init__(self, netmp, ip, port):
        self.prot = TsmpProt()

        super(Tsmp, self).__init__(ip, port)

        buffer = netmp.prot.register_cmd(netmp_key=netmp.netmp_key, reg_protocol=TsmpProt.PROTOCOL)
        buffer = self.sendrecv(buffer)
        buffer, res = netmp.prot.register_parse(buffer)
        
        if res["result"]:
            self.stop()
            raise self.NetmpException(res["result"])

    def get_conf(self):
        buffer = self.prot.get_conf_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_conf_parse(buffer)

        return res

    def get_info(self):
        buffer = self.prot.get_info_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_info_parse(buffer)

        return {item["name"]:item["value"] for item in res["data"]}

    def get_pict(self, mode):
        """ generator of image blocks in tga format.
        
            mode - AUTO - Whatever is showing
                   GAME - The current game process or VSH if no game running
                   SYSTEM - VSH
        """ 
        buffer = self.prot.get_pict_cmd(mode)

        for buffer in self.sendrecvmult(buffer):
            buffer, res = self.prot.get_pict_parse(buffer)
            if len(buffer) > 8:
                yield buffer
    
    def reboot(self):
        buffer = self.prot.power_control_cmd(TsmpProt.POWER_REBOOT)
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.power_control_parse(buffer)
        return res

    def power_off(self):
        buffer = self.prot.power_control_cmd(TsmpProt.POWER_OFF)
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.power_control_parse(buffer)
        return res

    def get_psn_state(self, username):
        buffer = self.prot.get_psn_state_cmd(username)
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.get_psn_state_parse(buffer)

        return res

    def get_power_status(self):
        buffer = self.prot.power_status_cmd()
        buffer = self.sendrecv(buffer)
        buffer, res = self.prot.power_status_parse(buffer)

        return res

class NetmpManager:
    """ Base class that lets subclasses share netmp instances by ip """
    _netmp = {}
    _count = {}
    _lock = threading.Lock()

    def startnetmp(self, ip):
        with self._lock:

            if ip not in self._netmp:
                self._netmp[ip] = Netmp(ip=ip)
                self._netmp[ip].connect()
                self._count[ip] = 0

            self._count[ip] += 1

        return self._netmp[ip]

    def stopnetmp(self, ip):
        with self._lock:

            if ip in self._netmp:
                self._count[ip] -= 1
                if self._count[ip] == 0:
                    self._netmp[ip].disconnect()
                    del self._netmp[ip]



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
import functools

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



def names(protocol, msgtype):
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
        if getattr(cls, fld) == msgtype:
            msgtypename = fld

    if not msgtypename:
        msgtypename = hex(msgtype)

    return protocolname, msgtypename

def summarize(buffer):
    protocol = struct.unpack_from("<L", buffer, 8)[0]
    msgtype = struct.unpack_from("<L", buffer, 16)[0]

    return "%s:%s" % names(protocol, msgtype)

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
# * Send a NETMP_CONNECT_CMD message on that socket
# * Receive the NETMP_CONNECT_RES response on that socket.  This will contain the "netmp key"
# * Create a second socket connection to port 8550 of the devkit
# * Send a NETMP_REGISTER_CMD message with the netmp key and the CTRLP protocol id (0x0002c000) on the new socket
# * Receive the NETMP_REGISTER_RES response on that socket.
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

    def _calldefault_cmd(self, command, *args, **kwargs):
        buffer = None
        if command in self.CMD_RULES.keys():
            for rule in self.CMD_RULES[command]:
                buffer = self.build_buffer(Deci4HProt.recorddefs[rule], **kwargs)

        return self.make_deci_cmd_header(buffer, command, self.PROTOCOL)

    def _calldefault_parse(self, command, buffer):

        buffer, res = self.parse_header(buffer)
        if command in self.PARSE_RULES.keys():
            for rule in self.PARSE_RULES[command]:
                buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs[rule], res)

        return buffer, res

    def __getattr__(self, name):
        if name.endswith("_cmd"):
            cmdname = name.upper()
            if hasattr(self, cmdname):
                return functools.partial(self._calldefault_cmd, getattr(self,cmdname))
        elif name.endswith("_parse"):
            cmdname = name[:-5].upper() + "RES"
            if hasattr(self, cmdname):
                return functools.partial(self._calldefault_parse, getattr(self,cmdname))

        raise AttributeError

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
            res - key/value pairs from previous parses new values inserted into this

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
                elif type == 2:
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
    def __init__(self, netmp, ip, port):
        self._ip = ip
        self._port = port
        self._streams = {}
        self._objects = {}

        self._responses = {}
        self._notifications = {}
        self._conditions = {}

        self._tosend = {}
        self._run = True
        self._sendlock = threading.Lock()
        self._recvlock = threading.Lock()

        self._workbuff = {}
        self._worklength = {}
        self._exception = None

        self._rwthread = threading.Thread(name="DeciQueue",
                                          target=self._readwrite,
                                          args=(self, 'dummy'))


        self._rwthread.start()

    def add_stream(self, obj, netmp):
        stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stream.connect((self._ip, self._port))
        self._streams[obj] = stream
        self._objects[stream] = obj

        self._notifications[obj] = []

        if netmp:
            buffer = netmp.prot.register_cmd(netmp_key=netmp.netmp_key, reg_protocol=obj.prot.PROTOCOL)
            buffer = self.sendrecv(obj, buffer)
            buffer, res = netmp.prot.register_parse(buffer)
            
            if res["result"]:
                if res["result"] == NetmpProt.DECI_NETMP_ERROR_INUSE:
                    raise Netmp.InUseException()
                elif res["result"]:
                    raise self.NetmpException(res["result"])


    def _abort(self, exception):

        for s in self._streams.values():
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                # the socket may already be in shutdown state when the last protocol was closed,
                # so ignore the exception that would then be thrown by shutdown()
                pass
            finally:
                s.close()   
                
        self._exception = exception

        self._streams = {}

        try:
            self._recvlock.release()
        except:
            pass
        try:
            self._sendlock.release()
        except:
            pass


    def _readwrite(self, *args, **kwargs):

        self._exception = None

        while self._run and not self._exception:
            respondevent = []

            rd,wr,ex = select.select(self._streams.values(), self._streams.values(), self._streams.values(), 0)

            for stream in ex:
                print("ACK!", ex)

            for stream in rd:
                obj = self._objects[stream]

                # To read a full message, we have to read 8 bytes to determin length, then
                # read the rest of the bytes until we reach length.  At any time in this
                # process, the current read could end.  We build the message in _workbuff
                # over potentionally multiple passes, with _worklength set once we've read 8
                if self._recvlock.acquire(blocking=False):
                    try:
                        if stream not in self._workbuff:
                            self._workbuff[stream] = {}
                            self._worklength[stream] = {}

                        # Reading the length (first read, or we haven't gotten 8 bytes yet)
                        if not self._workbuff[stream] or not self._worklength[stream]:
                            if not self._workbuff[stream]:
                                self._workbuff[stream] = stream.recv(8)
                            elif not self._worklength[stream]:
                                self._workbuff[stream] += stream.recv(8-len(self._workbuff[stream]))
                                
                            if len(self._workbuff[stream]) >= 8:
                                self._worklength[stream] = struct.unpack_from("<L", self._workbuff[stream], 4)[0]

                        # reading the rest of the message
                        else:
                            self._workbuff[stream] += stream.recv(self._worklength[stream]-len(self._workbuff[stream]))
                            if len(self._workbuff[stream]) == self._worklength[stream]:

                                result = struct.unpack_from("<L", self._workbuff[stream], 20)[0]
                                if log_level >= 1:
                                    print("RECV %d - %s (%s)" % (stream.fileno(),summarize(self._workbuff[stream]), hex(result)))
                                log( "RECV (%s):\n%s" % (stream, make_dump(self._workbuff[stream])) )

                                sequence = struct.unpack_from("<H", self._workbuff[stream], 12)[0]

                                #HACK: really should be pulling apart the messages based on the protocol definitions
                                protocol = struct.unpack_from("<L", self._workbuff[stream], 8)[0]
                                msgtype = struct.unpack_from("<L", self._workbuff[stream], 16)[0]

                                if names(protocol, msgtype)[1].endswith("NOTIFICATION"):

                                    self._notifications[obj].append(self._workbuff[stream])

                                    if protocol == NetmpProt.PROTOCOL and msgtype == NetmpProt.FORCE_DISCON_NOTIFICATION:
                                        return self._abort(Netmp.InUseException())
                                else:
                                    if sequence not in self._responses:
                                        self._responses[sequence] = []
                                    self._responses[sequence].append(self._workbuff[stream])
                                    respondevent.append(sequence)


                                self._workbuff[stream] = None
                                self._worklength[stream] = None
                    except Exception as e:
                        return self._abort(e)
                         
                    self._recvlock.release()

            # must happen here to avoid race condition with _recvlock
            for sequence in respondevent:
                if sequence in self._conditions:
                    condition = self._conditions[sequence]
                    condition.acquire()
                    condition.notify()
                    condition.release()

            for stream in wr:
                if self._sendlock.acquire(blocking=False):
                    try:
                        if stream in self._tosend and len(self._tosend[stream]) > 0:
                            if log_level >= 1:
                                print("SEND %d - %s" % (stream.fileno(),summarize(self._tosend[stream][0])))
                            log( "SEND (%s):\n%s" % (stream, make_dump(self._tosend[stream][0])) )
                            stream.send(self._tosend[stream][0])
                            self._tosend[stream].pop(0)

                    except Exception as e:
                        return self._abort(e)

                    self._sendlock.release()

    def stop(self):
        if self._run:
            self._run = False
            self._rwthread.join()

            for s in self._streams.values():
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except OSError:
                    # the socket may already be in shutdown state when the last protocol was closed,
                    # so ignore the exception that would then be thrown by shutdown()
                    pass
                finally:
                    s.close()   

    def send(self, prot, buffer, condition=None):
        if not self._run:
            return None

        if self._exception:
            raise self._exception


        sequence = struct.unpack_from("<H", buffer, 12)[0]

        with self._sendlock:
            if prot not in self._streams:
                return None # probably shut down
            
            if self._streams[prot] not in self._tosend:
                self._tosend[self._streams[prot]] = []

            self._tosend[self._streams[prot]].append(buffer)

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

    def sendrecvmult(self, prot, buffer):
        condition = threading.Condition()
        sequence = self.send(prot, buffer, condition)

        if not sequence:
            return None

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

    def sendrecv(self, prot, buffer):
        #todo: rework.  Should we paste allmultipart messages together?
        l = [b for b in self.sendrecvmult(prot, buffer)]
        if not l:
            return None

        if len(l) != 1:
            raise "Multipart message not expected"
            
        return l[0]

    def get_notification_messages(self, obj):
        with self._recvlock:
            if len(self._notifications[obj]) > 0:
                return self._notifications[obj].pop(0)
            return None


class DeciObj:

    def is_connected(self):
        if hasattr(self, "netmp"):
            return self.netmp._exception == None
        else:
            return self._exception == None

    def _calldefault(self, name, *args, **kwargs):
        buffer = getattr(self.prot, name + "_cmd")(*args, **kwargs)
        if hasattr(self, "netmp"):
            buffer = self.netmp.sendrecv(self, buffer)
        else:
            buffer = self.sendrecv(self, buffer)

        if not buffer:
            return None

        buffer, res = getattr(self.prot,name + "_parse")(buffer)
        return res

    def __getattr__(self, name):
        if hasattr(self.prot, name + "_cmd") and hasattr(self.prot, name + "_parse"):
            return functools.partial(self._calldefault, name)
        else:
            raise AttributeError

# Basic organization
# 
# Each protocol has two classes:
#
# FooProt - Derived from Deci4HProt, responsible for generating messages and parsing responses.
# Foo - Derived from DeciQueue; ties a stream to a protocol and presents method interface to caller
#
# FooProt organization:
# Set of constants in form *_* representing message ids
# Constant for protocol id
# methods for each message type:
# *_cmd method - returns a buffer formated as a message, takes values to apply as arguments
# *_parse method - Takes a buffer and parses the values into a key/value set

class NetmpProt(Deci4HProt):
    GET_CONF_CMD = 0x0
    GET_CONF_RES = 0x1
    CONNECT_CMD = 0x2
    CONNECT_RES = 0x3
    DISCONNECT_CMD = 0x4
    DISCONNECT_RES = 0x5
    REGISTER_CMD = 0x6
    REGISTER_RES = 0x7
    UNREGISTER_CMD = 0x8
    UNREGISTER_RES = 0x9
    FORCE_DISCONNECT_CMD = 0xa
    FORCE_DISCONNECT_RES = 0xb
    GET_REGISTERED_LIST_CMD = 0xe
    GET_REGISTERED_LIST_RES = 0xf
    FORCE_DISCON_NOTIFICATION = 0x41
    INVALPROTO_NOTIFICATION = 0xe2
    PROTOCOL = 0x40001000

    DECI_NETMP_ERROR_INUSE = 0x1006

    CMD_RULES = {
            CONNECT_CMD:["SceNetmpConnectCmd"],
            REGISTER_CMD:["SceNetmpRegisterCmd"],
            UNREGISTER_CMD:["SceNetmpUnregisterCmd"]
    }

    PARSE_RULES = {
            GET_CONF_RES:["SceDeciCommonConfig","SceGetConfCmd"],
            CONNECT_RES:["SceNetmpConnectRes"]
    }

    def get_registered_list_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceNetmpRegInfo"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return buffer, res



class CtrlpProt(Deci4HProt):
    GET_CONF_CMD = 0x0
    GET_CONF_RES = 0x1
    REC_START_CMD = 0x2
    REC_START_RES = 0x3
    REC_STOP_CMD = 0x4
    REC_STOP_RES = 0x5
    REC_DATA_NOTIFICATION = 0x7
    PLAY_START_CMD = 0x8
    PLAY_START_RES = 0x9
    PLAY_STOP_CMD = 0xA
    PLAY_STOP_RES = 0xB
    PLAY_DATA_CMD = 0xC
    PLAY_DATA_RES = 0xD
    PROTOCOL = 0x0002c000

    CMD_RULES = {
            REC_START_CMD:["SceCtrlpDevices"],
            PLAY_START_CMD:["SceCtrlpDevices"],
    }

    PARSE_RULES = {
            GET_CONF_RES:["SceDeciCommonConfig","SceGetConfCmd"],
            PLAY_DATA_RES:["SceCtrlpPlayDataRes"],
    }

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
            
        return self.make_deci_cmd_header(buffer, self.PLAY_DATA_CMD, self.PROTOCOL)


    def play_raw_data_cmd(self, block):
        buffer = self.build_buffer(Deci4HProt.recorddefs["SceCtrlpPlayCmd"], threshold=0)
        buffer += block
        buffer = self.make_deci_cmd_header(buffer, self.PLAY_DATA_CMD, self.PROTOCOL)
        return buffer

    def play_raw_data_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceCtrlpPlayDataRes"], res)
        return buffer, res

    def notification_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        if res['msgtype'] == CtrlpProt.REC_DATA_NOTIFICATION:
            pass

        return buffer, res

class TtypProt(Deci4HProt):
    """ Protocol for tty messages.  Note that merely registering this protocol will cause it to spit
        tty messages at you. """
    GET_CONF_CMD = 0x0
    GET_CONF_RES = 0x1
    TTY_IN_CMD = 0x2
    TTY_IN_RES = 0x3
    GET_PORT_STATES_CMD = 0x4
    GET_PORT_STATES_RES = 0x5
    SET_PORT_STATES_CMD = 0x7
    SET_PORT_STATES_RES = 0x8
    TTY_OUT_NOTIFICATION = 0x80
    IN_BUFF_READY_NOTIFICATION = 0x81
    IN_CLOSE_NOTIFICATION = 0x82
    FATALHEAD_NOTIFICATION = 0xE0
    INVALHEAD_NOTIFICATION = 0xE1
    INVALPROTO_NOTIFICATION = 0xE2
    PROTOCOL = 0x80003000

    CMD_RULES = {
    }

    PARSE_RULES = {
            GET_CONF_RES:["SceDeciCommonConfig","SceGetConfCmd"]
    }

    def get_port_states_parse(self, buffer):
        buffer, res = self.parse_header(buffer)
        if res['msgtype'] == self.GET_PORT_STATES_RES:
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
        if res['msgtype'] == TtypProt.TTY_OUT_NOTIFICATION:
            buffer = self.parse_buffer(buffer, Deci4HProt.recorddefs["SceTtypOut"], res)


        return buffer, res

class TsmpProt(Deci4HProt):
    GET_CONF_CMD = 0x0
    GET_CONF_RES = 0x1
    GET_INFO_CMD = 0x2
    GET_INFO_RES = 0x3
    POWER_CONTROL_CMD = 0x4
    POWER_CONTROL_RES = 0x5
    GET_POWER_STATUS_CMD = 0x6
    GET_POWER_STATUS_RES = 0x7
    GET_PICT_CMD = 0x18
    GET_PICT_RES = 0x19
    GET_PSN_STATE_CMD = 0x20
    GET_PSN_STATE_RES = 0x21
    PROTOCOL = 0x80004000

    POWER_OFF = 0x100
    POWER_REBOOT = 0x200

    CMD_RULES = {
            POWER_CONTROL_CMD:["SceTsmpPowerRequest"],
            GET_PICT_CMD:["SceTsmpGetPict"],
            GET_PSN_STATE_CMD:["SceTsmpGetPsnStateCmd"],
    }

    PARSE_RULES = {
            GET_CONF_RES:["SceDeciCommonConfig","SceGetConfCmd"],
            GET_POWER_STATUS_RES:["SceTsmpPowerState"],
            GET_PSN_STATE_RES:["SceTsmpGetPsnStateRes"],
    }

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

# TODO multiple inheritence is icky.  I should make the queue separate
class Netmp(DeciObj, DeciQueue):
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

        super(Netmp, self).__init__(None, ip, port)

        self.add_stream(self, None)

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
        if not hasattr(self, "client_id"):
            try:
                self.client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostbyname(socket.gethostname()))
            except socket.gaierror:
                self.client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostname())
            

        buffer = self.prot.connect_cmd(client_id=self.client_id, udpport=0)
        buffer = self.sendrecv(self, buffer)
        buffer, res = self.prot.connect_parse(buffer)

        self.netmp_key = res["netmp_key"]
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

            buffer = self.prot.unregister_cmd(reg_protocol=self._registered[cls].prot.PROTOCOL)
            buffer = self.sendrecv(self, buffer)
            buffer, res = self.prot.unregister_parse(buffer)

            return res


    def get_owner(self):
        res = self.get_registered_list()
        for l in res["data"]:
            if (l["protocol"] & 0x80000000) == 0:
                return l["owner"]

        return None
        
    def disconnect(self):
        res = self._calldefault("disconnect")

        if res:
            self.stop()

        return res

    def get_notification(self):

        buffer = super(Netmp,self).get_notification_messages(self)
        if not buffer:
            return None

        buffer, res = self.prot.parse_header(buffer)

        return res



class Ctrlp(DeciObj):
    def __init__(self, netmp, ip, port):
        self.prot = CtrlpProt()

        self.netmp = netmp

        self.netmp.add_stream(self, netmp)

    def read_raw_data(self):
        buffer = self.netmp.get_notification_messages(self)
        if buffer:
            buffer, res = self.prot.notification_parse(buffer)
            if res['msgtype'] == CtrlpProt.REC_DATA_NOTIFICATION:
                return buffer
            else:
                pass # need to save these somewhere

        return None

class Ttyp(DeciObj):
    def __init__(self, netmp, ip, port):
        self.prot = TtypProt()

        self.netmp = netmp

        self.netmp.add_stream(self, netmp)

    def read(self):
        """ Reads a tty message without blocking.  If no messages pending, returns None """

        buffer = self.netmp.get_notification_messages(self)
        if buffer:
            buffer, res = self.prot.notification_parse(buffer)
            if res['msgtype'] == TtypProt.TTY_OUT_NOTIFICATION:
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

         
class Tsmp(DeciObj):
    MODE_GAME = 0
    MODE_SYSTEM = 1
    MODE_AUTO = 2

    def __init__(self, netmp, ip, port):
        self.prot = TsmpProt()

        self.netmp = netmp

        self.netmp.add_stream(self, netmp)

    def get_pict(self, mode):
        """ generator of image blocks in tga format.
        
            mode - AUTO - Whatever is showing
                   GAME - The current game process or VSH if no game running
                   SYSTEM - VSH
        """ 
        buffer = self.prot.get_pict_cmd(mode=mode)

        for buffer in self.netmp.sendrecvmult(self, buffer):
            buffer, res = self.prot.get_pict_parse(buffer)
            if len(buffer) > 8:
                yield buffer
    
    def reboot(self):
        return self.power_control(TsmpProt.POWER_REBOOT)

    def power_off(self):
        return self.power_control(TsmpProt.POWER_OFF)


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



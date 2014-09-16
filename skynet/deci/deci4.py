#!/usr/bin/env python

import array
import getpass
import select
import socket
import struct
import sys
import threading
import time

if sys.version_info[0] < 3:
    raise Exception("Python 3 required")

enable_logging = False

def log(*args):
    if enable_logging:
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
class Deci4H:
    """ Common base class for protocol classes.  Not intended to be instatiated.  Used to contain common code.  """

    @staticmethod
    def pad_len(length, multiple):
        """ Return first multiple above length """

        if (length // multiple) * multiple != length:
            return ((length // multiple) + 1 ) * multiple
        return length

    class ParseException(Exception):

        def __init__(self, protocol, type, expprotocol, exptype):
            self.protocol = protocol
            self.type = type
            self.expprotocol = expprotocol
            self.exptype = exptype
             
        def __str__(self):
            return ("Unexpected message protocol %x type %x (expected %x and %x" % 
                            (self.protocol, self.type, self.expprotocol, self.exptype))

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
        "SceCtrlpGetConfCmd":[
            {"type":'<l', "length":4, "name":"in_buf_size"}
        ],
        "SceTtypGetConfCmd":[
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
                    res[f["name"]] = struct.unpack_from("<l", buffer, offset+8)[0]
                elif type == 1:
                    res[f["name"]] = struct.unpack_from("<L", buffer, offset+8)[0]
                if type == 2:
                    res[f["name"]] = struct.unpack_from("<q", buffer, offset+8)[0]
                elif type == 3:
                    res[f["name"]] = struct.unpack_from("<Q", buffer, offset+8)[0]
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

        buffer = self.build_buffer(Deci4H.recorddefs["SceDeciHeader"], version=0x41, protocol=protocol)
        buffer.extend(self.build_buffer(Deci4H.recorddefs["SceDeciUlpCmdHdr"], seqnumber=Deci4H.sequence, fraginfo=0, msgtype=message))
        Deci4H.sequence += 1

        if inbuff:
            buffer.extend(inbuff)

        self.set_length(buffer, Deci4H.recorddefs["SceDeciHeader"], len(buffer))

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
        buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciHeader"], res)
        buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciUlpResHdr"], res)

        return buffer, res

    def recv_core(self, stream, timeout=0):
        """ Turn the input stream into messages. 

            stream - socket to read on.
            timeout - time to wait for full message before returning.

            Returns buffer or None if nothing could be read before the timeout
        """

        rd,wr,ex = select.select([stream], [], [], timeout)

        if stream in rd:
            buffer = stream.recv(8)
            length = struct.unpack_from("<L", buffer, 4)[0]
            buffer += stream.recv(length-8)

            return buffer

        return None

        
    def sendrecv(self, stream, buffer):
        """ send a message and immediately read the response. """

        log( "Send (%s):\n%s" % (stream, make_dump(buffer)) )
        stream.send(buffer)
        buffer = self.recv_core(stream,30)
        log( "Recv (%s):\n%s" % (stream, make_dump(buffer)) )
        return buffer

    def parse_assert(self, bufferin, protocol, message):
        """ parse a message, but fail if it isn't what is expected """
        buffer, res = self.parse_header(bufferin)
        if res["protocol"] != protocol and res["protocol"] == NetmpProt.PROTOCOL:
            netmp_prot = NetmpProt()
            buffer, res = netmp_prot.parse(res, buffer)

        elif res["protocol"] != protocol or res["msgtype"] != message:
            raise self.ParseException(res["protocol"], res["msgtype"], protocol, message)

        return self.parse(res, buffer)[1]

# Basic organization
# 
# Each protocol has two classes:
#
# FooProt - Derived from Deci4H, responsible for generating messages and parsing responses.
# Foo - Ties a stream to a protocol and presents method interface to caller
#
# FooProt organization:
# Set of constants in form SCE_*_TYPE_* representing message ids
# Constant for protocol id
# methods for each message type:
# *_cmd method - returns a buffer formated as a message, takes values to apply as arguments
# *_msg method - formats a message, sends it, then waits for the expected response, parsing and returning it
# parse - Parses all responses that are expected

class NetmpProt(Deci4H):
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
    SCE_NETMP_TYPE_INVALPROTO_NOTIFICATION = 0xe2
    PROTOCOL = 0x40001000

    SCE_DECI_NETMP_ERROR_INUSE = 0x1006

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_conf_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_GET_CONF_RES)

    def connect_cmd(self, client_id, udpport):

        buffer = self.build_buffer(Deci4H.recorddefs["SceNetmpConnectCmd"], client_id=client_id, udpport=udpport)
        buffer = self.make_deci_cmd_header(buffer, self.SCE_NETMP_TYPE_CONNECT_CMD, self.PROTOCOL)

        return buffer

    def connect_msg(self, stream, client_id, udpport):
        buffer = self.sendrecv(stream, self.connect_cmd(client_id, udpport))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_CONNECT_RES)

    def disconnect_cmd(self):

        buffer = self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_DISCONNECT_CMD, self.PROTOCOL)

        return buffer

    def disconnect_msg(self, stream):
        buffer = self.sendrecv(stream, self.disconnect_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_DISCONNECT_RES)

    def force_disconnect_cmd(self):

        buffer = self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_FORCE_DISCONNECT_CMD, self.PROTOCOL)

        return buffer

    def force_disconnect_msg(self, stream):
        buffer = self.sendrecv(stream, self.force_disconnect_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_FORCE_DISCONNECT_RES)

    def register_cmd(self, netmp_key, reg_protocol):

        buffer = self.build_buffer(Deci4H.recorddefs["SceNetmpRegisterCmd"], netmp_key=netmp_key, reg_protocol=reg_protocol)
        buffer = self.make_deci_cmd_header(buffer, self.SCE_NETMP_TYPE_REGISTER_CMD, self.PROTOCOL)

        return buffer

    def register_msg(self, stream, netmp_key, reg_protocol):
        buffer = self.sendrecv(stream, self.register_cmd(netmp_key, reg_protocol))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_REGISTER_RES)

    def unregister_cmd(self, reg_protocol):

        buffer = self.build_buffer(Deci4H.recorddefs["SceNetmpUnregisterCmd"], reg_protocol=reg_protocol)
        buffer = self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_UNREGISTER_CMD, self.PROTOCOL)

        return buffer

    def unregister_msg(self, stream, reg_protocol):
        buffer = self.sendrecv(stream, self.unregister_cmd(reg_protocol))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_NETMP_TYPE_UNREGISTER_RES)

    def get_registered_list_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_NETMP_TYPE_GET_REGISTERED_LIST_CMD, self.PROTOCOL)

    def get_registered_list_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_registered_list_cmd())
        buffer, res = self.parse_header(buffer)
        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceNetmpRegInfo"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return res

    def parse(self, res, buffer):
        if res["msgtype"] == self.SCE_NETMP_TYPE_GET_CONF_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciCommonConfig"], res)
        elif res["msgtype"] == self.SCE_NETMP_TYPE_CONNECT_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceNetmpConnectRes"], res)
        elif res["msgtype"] == self.SCE_NETMP_TYPE_INVALPROTO_NOTIFICATION:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciUlpNtfHdr"], res)
        elif (res["msgtype"] == self.SCE_NETMP_TYPE_REGISTER_RES or 
              res["msgtype"] == self.SCE_NETMP_TYPE_UNREGISTER_RES or
              res["msgtype"] == self.SCE_NETMP_TYPE_DISCONNECT_RES or
              res["msgtype"] == self.SCE_NETMP_TYPE_FORCE_DISCONNECT_RES):
            pass

        return buffer, res


class CtrlpProt(Deci4H):
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

    def get_conf_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_conf_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_GET_CONF_RES)

    def rec_start_cmd(self, controller=0xffffffff):
        buffer = self.build_buffer(Deci4H.recorddefs["SceCtrlpDevices"], controller=controller)
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_REC_START_CMD, self.PROTOCOL)

    def rec_start_msg(self, stream, controller=0xffffffff):
        buffer = self.sendrecv(stream, self.rec_start_cmd(controller))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_REC_START_RES)

    def rec_stop_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_CTRLP_TYPE_REC_STOP_CMD, self.PROTOCOL)

    def rec_stop_msg(self, stream):
        buffer = self.sendrecv(stream, self.rec_stop_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_REC_STOP_RES)

    def play_start_cmd(self, controller=0xffffffff):
        buffer = self.build_buffer(Deci4H.recorddefs["SceCtrlpDevices"], controller=controller)
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_START_CMD, self.PROTOCOL)

    def play_start_msg(self, stream, controller=0xffffffff):
        buffer = self.sendrecv(stream, self.play_start_cmd(controller))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_PLAY_START_RES)

    def play_data_cmd(self, events):
        if len(events) > 8:
            raise self.PlayException(len(events))

        buffer = self.build_buffer(Deci4H.recorddefs["SceCtrlpPlayCmd"], threshold=0)

        timeoff = 0
        for button in events:
            buffer.extend(self.build_buffer(Deci4H.recorddefs["SceCtrlpData"], 
                size = 56,
                timestamp = timeoff,
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

            timeoff += 0  # not sure what this does if not zero.  Seems to have no effect
            
        return self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_DATA_CMD, self.PROTOCOL)

    def play_data_msg(self, stream, events):
        buffer = self.sendrecv(stream, self.play_data_cmd(events))
        res = self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_PLAY_DATA_RES)

        # if result is 1, we've filled memory.  Could wait and retry
        if res["result"] != 0:
            raise self.NetmpException(res["result"])

        return res

    def play_raw_data_cmd(self, block):
        buffer = self.build_buffer(Deci4H.recorddefs["SceCtrlpPlayCmd"], threshold=0)
        buffer += block
        buffer = self.make_deci_cmd_header(buffer, self.SCE_CTRLP_TYPE_PLAY_DATA_CMD, self.PROTOCOL)
        return buffer

    def play_raw_data_msg(self, stream, block):
        while True:
            buffer = self.sendrecv(stream, self.play_raw_data_cmd(block))
            res = self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_PLAY_DATA_RES)

            # if result is 1, we've filled memory.  Wait and retry
            if res["result"] != 1:
                # check errors!
                break

            time.sleep(0.01)

        return res

    def play_stop_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_CTRLP_TYPE_PLAY_STOP_CMD, self.PROTOCOL)

    def play_stop_msg(self, stream):
        buffer = self.sendrecv(stream, self.play_stop_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_CTRLP_TYPE_PLAY_STOP_RES)

    def parse(self, res, buffer):
        if res["msgtype"] == self.SCE_CTRLP_TYPE_GET_CONF_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciCommonConfig"], res)
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceCtrlpGetConfCmd"], res)
        elif res["msgtype"] == self.SCE_CTRLP_TYPE_PLAY_DATA_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceCtrlpPlayDataRes"], res)
        elif (res["msgtype"] == self.SCE_CTRLP_TYPE_REC_START_RES or 
              res["msgtype"] == self.SCE_CTRLP_TYPE_REC_STOP_RES or
              res["msgtype"] == self.SCE_CTRLP_TYPE_PLAY_START_RES or
              res["msgtype"] == self.SCE_CTRLP_TYPE_PLAY_STOP_RES ):
            pass

        return buffer, res

    def read_data(self, stream):
        buffer = self.recv_core(stream,30)

        log( "Recv (%s):\n%s" % (stream, make_dump(buffer)) )
        buffer, res = self.parse_header(buffer)

        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceCtrlpData"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return res

    def read_raw_data(self, stream):
        buffer = self.recv_core(stream,30)
        log( "Recv (%s):\n%s" % (stream, make_dump(buffer)) )
        return self.parse_header(buffer)[0]

class TtypProt(Deci4H):
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

    def get_conf_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_conf_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TTYP_TYPE_GET_CONF_RES)

    def get_port_states_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TTYP_TYPE_GET_PORT_STATES_CMD, self.PROTOCOL)

    def get_port_states_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_port_states_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TTYP_TYPE_GET_PORT_STATES_RES)

    def parse(self, res, buffer):
        if res["msgtype"] == self.SCE_TTYP_TYPE_GET_CONF_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciCommonConfig"], res)
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTtypGetConfCmd"], res)

        elif res["msgtype"] == self.SCE_TTYP_TYPE_GET_PORT_STATES_RES:
            res["data"] = []
            elements = struct.unpack_from("<l", buffer, 0)[0]
            buffer = buffer[8:] # skip num elements and elment size

            for i in range(elements):
                resdata = {}
                buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTtypPortState"], resdata)
                res["data"].append(resdata)

        elif res["msgtype"] == self.SCE_TTYP_TYPE_TTY_OUT_NOTIFICATION:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTtypOut"], res)
        else:
            pass

        return buffer, res

    def recv(self, stream):
        buffer = self.recv_core(stream)
        if not buffer:
            return None

        return buffer

class TsmpProt(Deci4H):
    SCE_TSMP_TYPE_GET_CONF_CMD = 0x0
    SCE_TSMP_TYPE_GET_CONF_RES = 0x1
    SCE_TSMP_TYPE_GET_INFO_CMD = 0x2
    SCE_TSMP_TYPE_GET_INFO_RES = 0x3
    SCE_TSMP_TYPE_POWER_CONTROL_CMD = 0x4
    SCE_TSMP_TYPE_POWER_CONTROL_RES = 0x5
    SCE_TSMP_TYPE_GET_POWER_STATUS_CMD = 0x6
    SCE_TSMP_TYPE_GET_POWER_STATUS_RES = 0x7
    SCE_TSMP_TYPE_GET_PSN_STATE_CMD = 0x20
    SCE_TSMP_TYPE_GET_PSN_STATE_RES = 0x21
    PROTOCOL = 0x80004000

    POWER_OFF = 0x100
    POWER_REBOOT = 0x200

    def get_conf_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_CONF_CMD, self.PROTOCOL)

    def get_conf_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_conf_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TSMP_TYPE_GET_CONF_RES)

    def get_info_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_INFO_CMD, self.PROTOCOL)

    def get_info_msg(self, stream):
        buffer = self.sendrecv(stream, self.get_info_cmd())
        buffer, res = self.parse_header(buffer)

        res["data"] = []
        terminator = struct.unpack_from("<l", buffer, 0)[0]
        while(terminator > 0):
            resdata = {}
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTsmpNameValueDisplay"], resdata)
            res["data"].append(resdata)
            terminator = struct.unpack_from("<l", buffer, 0)[0]

        return res

    def power_control_cmd(self, powerstate):
        buffer = self.build_buffer(Deci4H.recorddefs["SceTsmpPowerRequest"], powerstate=powerstate)
        return self.make_deci_cmd_header(buffer, self.SCE_TSMP_TYPE_POWER_CONTROL_CMD, self.PROTOCOL)
        
    def power_control_msg(self, stream, powerstate):
        buffer = self.sendrecv(stream, self.power_control_cmd(powerstate))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TSMP_TYPE_POWER_CONTROL_RES)

    def power_status_cmd(self):
        return self.make_deci_cmd_header(None, self.SCE_TSMP_TYPE_GET_POWER_STATUS_CMD, self.PROTOCOL)

    def power_status_msg(self, stream):
        buffer = self.sendrecv(stream, self.power_status_cmd())
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TSMP_TYPE_GET_POWER_STATUS_RES)        

    def get_psn_state_cmd(self, username):
        buffer = self.build_buffer(Deci4H.recorddefs["SceTsmpGetPsnStateCmd"], username=username)
        return self.make_deci_cmd_header(buffer, self.SCE_TSMP_TYPE_GET_PSN_STATE_CMD, self.PROTOCOL)
        
    def get_psn_state_msg(self, stream, username):
        buffer = self.sendrecv(stream, self.get_psn_state_cmd(username))
        return self.parse_assert(buffer, self.PROTOCOL, self.SCE_TSMP_TYPE_GET_PSN_STATE_RES)

    def parse(self, res, buffer):
        if res["msgtype"] == self.SCE_TSMP_TYPE_GET_CONF_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciCommonConfig"], res)
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTtypGetConfCmd"], res)
        elif res["msgtype"] == self.SCE_TSMP_TYPE_GET_PSN_STATE_RES:
            if res["result"] == 0:
                buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTsmpGetPsnStateRes"], res)
        elif res["msgtype"] == self.SCE_TSMP_TYPE_POWER_CONTROL_RES:
            pass

        elif res["msgtype"] == self.SCE_TSMP_TYPE_GET_POWER_STATUS_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceTsmpPowerState"], res)
            
        return buffer, res

class Netmp:
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
        self.ip = ip
        self.port = port
        self.stream1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream1.connect((self.ip, self.port))
        self._counts = {}

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

    def connect(self):
        try:
            client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostbyname(socket.gethostname()))
        except socket.gaierror:
            client_id = "%s@%s,EXDGDECI4" % ( getpass.getuser(), socket.gethostname())
            
        res = self.prot.connect_msg(self.stream1, client_id=client_id, udpport=0)
        self.netmp_key = res["netmp_key"]

        #checkexception

    def get_conf(self):
        return self.prot.get_conf_msg(self.stream1)

    def register_ttyp(self):
        if self._refcnt_inc("ttyp"):
            self.stream_ttyp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream_ttyp.connect((self.ip, self.port))

            res = self.prot.register_msg(self.stream_ttyp, netmp_key=self.netmp_key, reg_protocol=TtypProt.PROTOCOL)

            #checkexception

        return Ttyp(self.stream_ttyp)

    def unregister_ttyp(self):
        if self._refcnt_dec("ttyp"):
            res = self.prot.unregister_msg(self.stream1, reg_protocol=TtypProt.PROTOCOL)

            #checkexception

            self.stream_ttyp.shutdown(socket.SHUT_RDWR)
            self.stream_ttyp.close()

    def register_ctrlp(self):
        if self._refcnt_inc("ctrlp"):
            self.stream_ctrlp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream_ctrlp.connect((self.ip, self.port))

            res = self.prot.register_msg(self.stream_ctrlp, netmp_key=self.netmp_key, reg_protocol=CtrlpProt.PROTOCOL)

            if res["result"] == NetmpProt.SCE_DECI_NETMP_ERROR_INUSE:
                raise self.InUseException()
            elif res["result"]:
                raise self.NetmpException(res["result"])

            #checkexception

        return Ctrlp(self.stream_ctrlp)

    def unregister_ctrlp(self):
        if self._refcnt_dec("ctrlp"):
            res = self.prot.unregister_msg(self.stream1, reg_protocol=CtrlpProt.PROTOCOL)

            #checkexception

            self.stream_ctrlp.shutdown(socket.SHUT_RDWR)
            self.stream_ctrlp.close()

    def register_tsmp(self):
        if self._refcnt_inc("tsmp"):
            self.stream_tsmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream_tsmp.connect((self.ip, self.port))

            res = self.prot.register_msg(self.stream_tsmp, netmp_key=self.netmp_key, reg_protocol=TsmpProt.PROTOCOL)
            self.count_tsmp = 0

            #checkexception

        return Tsmp(self.stream_tsmp)

    def unregister_tsmp(self):
        if self._refcnt_dec("tsmp"):
            res = self.prot.unregister_msg(self.stream1, reg_protocol=TsmpProt.PROTOCOL)

            #checkexception

            self.stream_tsmp.shutdown(socket.SHUT_RDWR)
            self.stream_tsmp.close()

    def force_disconnect(self):
        res = self.prot.force_disconnect_msg(self.stream1)
        
    def get_registered_list(self):
        return self.prot.get_registered_list_msg(self.stream1)

    def get_owner(self):
        res = self.prot.get_registered_list_msg(self.stream1)
        for l in res["data"]:
            if l["protocol"] | 0x80000000 != 0:
                return l["owner"]

        return None
        
    def disconnect(self):
        res = self.prot.disconnect_msg(self.stream1)

        #checkexception

        try:
            self.stream1.shutdown(socket.SHUT_RDWR)
        except OSError:
            # the socket may already be in shutdown state when the last protocol was closed,
            # so ignore the exception that would then be thrown by shutdown()
            pass
        finally:
            self.stream1.close()


class Ctrlp:
    def __init__(self, stream):
        self.prot = CtrlpProt()
        self.stream = stream

    def get_conf(self):
        return self.prot.get_conf_msg(self.stream)

    def rec_start(self):
        self.prot.rec_start_msg(self.stream)

    def rec_stop(self):
        self.prot.rec_stop_msg(self.stream)

    def read_data(self):
        return self.prot.read_data(self.stream)

    def read_raw_data(self):
        return self.prot.read_raw_data(self.stream)

    def play_start(self):
        rc = self.prot.play_start_msg(self.stream)

    def play_data(self, events):
        self.prot.play_data_msg(self.stream, events)

    def play_raw_data(self, events):
        self.prot.play_raw_data_msg(self.stream, events)

    def play_stop(self):
        self.prot.play_stop_msg(self.stream)

class Ttyp:
    def __init__(self, stream):
        self.prot = TtypProt()
        self.stream = stream

    def get_conf(self):
        return self.prot.get_conf_msg(self.stream)

    def get_port_states(self):
        return self.prot.get_port_states_msg(self.stream)

    def read(self):
        """ Reads a tty message without blocking.  If no messages pending, returns None """
        buffer = self.prot.recv(self.stream)

        if not buffer:
            return None

        buffer, res = self.prot.parse_header(buffer)
        buffer, res = self.prot.parse(res,buffer)

        return res
                
    def readsync(self):
        rd,wr,ex = select.select([self.stream], [], [], 30)
        return self.read()
        

class Tsmp:
    def __init__(self, stream):
        self.prot = TsmpProt()
        self.stream = stream

    def get_conf(self):
        return self.prot.get_conf_msg(self.stream)

    def get_info(self):
        info = self.prot.get_info_msg(self.stream)
        return {item["name"]:item["value"] for item in info["data"]}
    
    def reboot(self):
        return self.prot.power_control_msg(self.stream, TsmpProt.POWER_REBOOT)

    def power_off(self):
        return self.prot.power_control_msg(self.stream, TsmpProt.POWER_OFF)

    def get_psn_state(self, username):
        return self.prot.get_psn_state_msg(self.stream, username)

    def get_power_status(self):
        return self.prot.power_status_msg(self.stream) 

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



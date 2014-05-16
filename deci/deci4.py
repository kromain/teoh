#!/usr/bin/env python

import socket
import array
import struct
import getpass
import time

enable_logging = False

def log(*args):
    if enable_logging:
        log_string = ''
        for arg in args:
            log_string += str(arg)
        if (len(log_string)):
            print( log_string )
    return

    
def chunker(l,n):
    for i in xrange(0,len(l),n):
        yield l[i:i+n]

def makewords(l):
    for i in xrange(0,len(l),2):
        s = l[i][2:]

        if i+1 < len(l):
            s += l[i+1][2:].zfill(2)

        yield s.zfill(4)

def ascdisp(b):
    x = int(b,16)
    
    if x < 32 or x > 127:
        return '.'
    else:
        return chr(x)
         
def make_dump(bytes):

    if type(bytes) is str:
        bytes = [ord(x) for x in bytes]

    rc = ""
    for addr, line in enumerate(chunker(map(hex, bytes), 16)):
        rc += "%6s: %-39s %s\n" % (hex(addr * 16),
                                  ' '.join(makewords(line)),
                                  ''.join(map(ascdisp,line)))
    return rc


def pad_len(bytes, multiple):
    if (bytes / multiple) * multiple != bytes:
        return ((bytes / multiple) + 1 ) * multiple
    return bytes



class ParseException(Exception):

    def __init__(self, protocol, type):
        self.protocol = protocol
        self.type = type
         
    def __str__(self):
        return "Unexpected message protocol %x type %x" % (self.protocol, self.type)

class PlayException(Exception):
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return "You set the length to %d but the max is 8.  This will cause the playback system to bork, and you'll need to reboot, so don't do that" % self.length

class Deci4H:
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
            #{"type":'<l', "length":4, "name":"foo"},  # found by inspection
            {"type":'zeros', "length":4},
            {"type":"SceDeciStringUtf8", "name":"client_id"},
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
        "SceCtrlpGetConfCmd":[
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
        ]
    }
    sequence = 0x1234

    def build_buffer(self, format, **kwargs):

        for f in format:
            if f["type"] == "SceDeciStringUtf8":
                f["length"] = len(kwargs[f["name"]]) + 4

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
                    struct.pack_into("%ds" % len(val), buffer, offset+4, val)


            offset += f["length"]

        return buffer

    def set_length(sef, buffer, format, length):
        offset = 0
        for f in format:
            if f["type"] != "zeros":
                if f["name"] == "length":
                    struct.pack_into(f["type"], buffer, offset, length)

            offset = offset + f["length"]
        
    def parse_buffer(self, buffer, format, res):
        offset = 0
        for f in format:
            if f["type"] != "zeros":
                res[f["name"]] = struct.unpack_from(f["type"], buffer, offset)[0]

            offset += f["length"]

        return buffer[offset:]

    def make_deci_cmd_header(self, inbuff, message, protocol):

        buffer = self.build_buffer(Deci4H.recorddefs["SceDeciHeader"], version=0x41, protocol=protocol)
        buffer.extend(self.build_buffer(Deci4H.recorddefs["SceDeciUlpCmdHdr"], seqnumber=Deci4H.sequence, fraginfo=0, msgtype=message))
        Deci4H.sequence += 1

        if inbuff:
            buffer.extend(inbuff)

        self.set_length(buffer, Deci4H.recorddefs["SceDeciHeader"], len(buffer))

        return buffer

    def parse_header(self, buffer):
        res = {}
        buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciHeader"], res)
        buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciUlpResHdr"], res)

        return buffer, res


    def sendrecv(self, stream, buffer):
        log( "Send (%s):\n%s" % (stream, make_dump(buffer)) )
        stream.send(buffer)
        buffer = stream.recv(1024)
        log( "Recv (%s):\n%s" % (stream, make_dump(buffer)) )
        return buffer

    def parse_assert(self, buffer, protocol, message):
        buffer, res = self.parse_header(buffer)
        if res["protocol"] != protocol or res["msgtype"] != message:
            raise ParseException(res["protocol"], res["msgtype"])

        return self.parse(res, buffer)[1]

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
    PROTOCOL = 0x40001000

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

    def parse(self, res, buffer):
        if res["msgtype"] == self.SCE_NETMP_TYPE_GET_CONF_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceDeciCommonConfig"], res)
        elif res["msgtype"] == self.SCE_NETMP_TYPE_CONNECT_RES:
            buffer = self.parse_buffer(buffer, Deci4H.recorddefs["SceNetmpConnectRes"], res)
        elif (res["msgtype"] == self.SCE_NETMP_TYPE_REGISTER_RES or 
              res["msgtype"] == self.SCE_NETMP_TYPE_UNREGISTER_RES or
              res["msgtype"] == self.SCE_NETMP_TYPE_DISCONNECT_RES):
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
            raise PlayException(len(events))

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
            print "Oh noes!", res["result"]

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
        buffer = stream.recv(1024)
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
        buffer = stream.recv(1024)
        log( "Recv (%s):\n%s" % (stream, make_dump(buffer)) )
        return self.parse_header(buffer)[0]


class Netmp:
    def __init__(self, ip, port=8550):
        self.prot = NetmpProt()
        self.ip = ip
        self.port = port
        self.stream1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream1.connect((self.ip, self.port))

    def connect(self):
        client_id = "%s@%s, EXDGDECI4" % ( getpass.getuser(), socket.gethostbyname(socket.gethostname()))
        res = self.prot.connect_msg(self.stream1, client_id=client_id, udpport=0)
        self.netmp_key = res["netmp_key"]

        #checkexception

    def get_conf(self):
        return self.prot.get_conf_msg(self.stream1)

    def register_ctrlp(self):
        self.stream2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream2.connect((self.ip, self.port))

        res = self.prot.register_msg(self.stream2, netmp_key=self.netmp_key, reg_protocol=CtrlpProt.PROTOCOL)

        #checkexception
        return Ctrlp(self.stream2)

    def unregister_ctrlp(self):
        res = self.prot.unregister_msg(self.stream1, reg_protocol=CtrlpProt.PROTOCOL)

        #checkexception
        
    def disconnect(self):
        res = self.prot.disconnect_msg(self.stream1)

        #checkexception

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
        self.prot.play_start_msg(self.stream)

    def play_data(self, events):
        self.prot.play_data_msg(self.stream, events)

    def play_raw_data(self, events):
        self.prot.play_raw_data_msg(self.stream, events)

    def play_stop(self):
        self.prot.play_stop_msg(self.stream)



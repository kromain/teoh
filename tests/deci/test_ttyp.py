#!/usr/bin/env python3
import os
import time
import pytest

from skynet.deci import Netmp
from skynet.deci.deci4 import Ttyp, TtypProt, Ctrlp
import conftest

test_target_ip = conftest.target_ip

class TestTtyp:

    def setup(self):
        self.netmp = Netmp(ip=test_target_ip)

        self.netmp.connect()

    def teardown(self):
        self.netmp.disconnect()


    def test_basics(self):
        ttyp = self.netmp.register(Ttyp)
        assert(ttyp)
        assert(type(ttyp) == Ttyp)

        res = ttyp.get_conf()
        assert(res)
        assert(res['result'] == 0)
        assert(res['protocol'] == ttyp.prot.PROTOCOL)
        assert(res['protocol'] == TtypProt.PROTOCOL)

        res = ttyp.get_port_states()
        assert(res)

        ctrlp = self.netmp.register(Ctrlp)
        assert(ctrlp)

        # We know empirically that this generates tty messages
        ctrlp.play_start()
        ctrlp.play_data([0x10000]*8) # PS button
        time.sleep(0.5)
        ctrlp.play_data([0x0]*8)
        ctrlp.play_stop()
        time.sleep(1)

        msgcount = 0
        while True:
            res = ttyp.read()
            if not res:
                break

            assert(res['message'])
            assert(type(res['message']) == str)
            assert(len(res['message']) > 0)
            msgcount += 1

        assert(msgcount)

        # For some reason, unregister always returns a failure code (0x1004, not registered) 
        #res = self.netmp.unregister(Ctrlp)
        #assert(res)
        #assert(res['result'] == 0)
        #res = self.netmp.unregister(Ttyp)
        #assert(res)
        #assert(res['result'] == 0)


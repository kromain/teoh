#!/usr/bin/env python3
import os
import time
import pytest

from skynet.deci import Netmp
from skynet.deci.deci4 import Tsmp, Ttyp, Ctrlp, NetmpProt
import conftest

test_target_ip = conftest.target_ip

class TestScreenshot:

    def setup(self):
        pass

    def teardown(self):
        pass


    def test_basics(self):
        netmp = Netmp(ip=test_target_ip)

        res = netmp.connect()
        assert(res)
        assert(res['result'] == 0)

        res = netmp.get_conf()
        assert(res)
        assert(res['result'] == 0)
        assert(res['protocol'] == netmp.prot.PROTOCOL)
        assert(res['protocol'] == NetmpProt.PROTOCOL)

        tsmp = netmp.register(Tsmp)
        assert(tsmp)
        assert(type(tsmp) == Tsmp)

        tsmp2 = netmp.register(Tsmp)
        assert(tsmp2)
        assert(type(tsmp2) == Tsmp)
        assert(tsmp2 is tsmp)

        ctrlp = netmp.register(Ctrlp)
        assert(ctrlp)
        assert(type(ctrlp) == Ctrlp)

        ttyp = netmp.register(Ttyp)
        assert(ttyp)
        assert(type(ttyp) == Ttyp)


        res = netmp.unregister(Tsmp)
        assert(res == None)

        # For some reason, unregister always returns a failure code (0x1004, not registered) 
        #res = netmp.unregister(Tsmp)
        #assert(res)
        #assert(res['result'] == 0)
        #res = netmp.unregister(Ttyp)
        #assert(res)
        #assert(res['result'] == 0)
        #res = netmp.unregister(Ctrlp)
        #assert(res)
        #assert(res['result'] == 0)

        res = netmp.disconnect()
        assert(res)
        assert(res['result'] == 0)

    def test_nonmulti(self):
        netmp = Netmp(ip=test_target_ip)
        res = netmp.connect()

        netmp2 = Netmp(ip=test_target_ip)
        res = netmp2.connect()

        tsmp = netmp.register(Tsmp)
        tsmp2 = netmp2.register(Tsmp)
        assert(tsmp2 is not tsmp)

        ttyp = netmp.register(Ttyp)
        ttyp2 = netmp2.register(Ttyp)
        assert(ttyp2 is not ttyp)

        res = netmp.disconnect()
        assert(res)
        assert(res['result'] == 0)

        res = netmp2.disconnect()
        assert(res)
        assert(res['result'] == 0)

    def test_multi(self):
        netmp = Netmp(ip=test_target_ip)
        res = netmp.connect()

        res = netmp.get_owner()
        assert(res == None)

        netmp2 = Netmp(ip=test_target_ip)
        res = netmp2.connect()

        ctrlp = netmp.register(Ctrlp)

        res = netmp.get_registered_list()
        assert(res)
        assert(res['result'] == 0)

        # for some reason, cannot set owner to fixed value
        res = netmp.get_owner()
        assert(res)
        assert(type(res) == str)

        res2 = netmp.get_owner()
        assert(res2)
        assert(type(res2) == str)
        assert(res == res2)

        with pytest.raises(Netmp.InUseException):
            ctrlp2 = netmp2.register(Ctrlp)

        # Works but leaves netmp thread in a bad state
        # This is because netmp does not yet do proper error response
        #res = netmp2.force_disconnect()
        #assert(res)
        #assert(res['result'] == 0)
        #ctrlp2 = netmp2.register(Ctrlp)
        #assert(ctrlp2)

        res = netmp.disconnect()
        assert(res)
        assert(res['result'] == 0)

        res = netmp2.disconnect()
        assert(res)
        assert(res['result'] == 0)

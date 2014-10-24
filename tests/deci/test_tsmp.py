#!/usr/bin/env python3
import os
import time
import pytest

from skynet.deci import Netmp
from skynet.deci.deci4 import Tsmp, TsmpProt
import conftest

test_target_ip = conftest.target_ip

class TestTsmp:

    def setup(self):
        self.netmp = Netmp(ip=test_target_ip)

        self.netmp.connect()

    def teardown(self):
        self.netmp.disconnect()


    def test_basics(self):
        tsmp = self.netmp.register(Tsmp)
        assert(tsmp)
        assert(type(tsmp) == Tsmp)

        res = tsmp.get_conf()
        assert(res)
        assert(res['result'] == 0)
        assert(res['protocol'] == tsmp.prot.PROTOCOL)
        assert(res['protocol'] == TsmpProt.PROTOCOL)

        res = tsmp.get_info()
        assert(type(res) == dict)

        cnt = 0
        for block in tsmp.get_pict(2):
            cnt += 1
            if cnt == 127:
                assert( len(block) == 36892 )
            else:
                assert( len(block) == 65536 )

        assert(cnt == 127)

        res = tsmp.get_psn_state(username="steve-e1")
        assert(res)
        assert(res['result'] == 0)
        assert(res['psnState'] == 2 or res['psnState'] == 1)

        res = tsmp.get_power_status()
        assert(res)
        assert(res['result'] == 0)
        assert(res['powerState'] in [1,2,3,4,5,6,7,8])

        res = self.netmp.unregister(Tsmp)
        assert(res)
        assert(res['result'] == 0)


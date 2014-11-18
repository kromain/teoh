#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

from skynet.deci.deci4 import Tsmp, TsmpProt


def test_basics(netmp):
    tsmp = netmp.register(Tsmp)
    assert tsmp
    assert(type(tsmp) == Tsmp)

    res = tsmp.get_conf()
    assert res
    assert(res['result'] == 0)
    assert(res['protocol'] == tsmp.prot.PROTOCOL)
    assert(res['protocol'] == TsmpProt.PROTOCOL)

    res = tsmp.get_info()
    assert(type(res) == dict)

    cnt = 0
    for block in tsmp.get_pict(2):
        cnt += 1
        if cnt == 127:
            assert(len(block) == 36892)
        else:
            assert(len(block) == 65536)

    assert(cnt == 127)

    res = tsmp.get_psn_state(username="steve-e1")
    assert res
    if res['result'] == 0:
        assert (res['psnState'] == 2 or res['psnState'] == 1)

    res = tsmp.get_power_status()
    assert res
    assert(res['result'] == 0)
    assert(res['powerState'] in [1, 2, 3, 4, 5, 6, 7, 8])

    res = netmp.unregister(Tsmp)
    assert res
    assert(res['result'] == 0)

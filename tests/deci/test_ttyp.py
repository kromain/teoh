#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import time

from skynet.deci.deci4 import Ttyp, TtypProt, Ctrlp


def test_basics(netmp):
    ttyp = netmp.register(Ttyp)
    assert ttyp
    assert(type(ttyp) == Ttyp)

    res = ttyp.get_conf()
    assert res
    assert(res['result'] == 0)
    assert(res['protocol'] == ttyp.prot.PROTOCOL)
    assert(res['protocol'] == TtypProt.PROTOCOL)

    res = ttyp.get_port_states()
    assert res

    ctrlp = netmp.register(Ctrlp)
    assert ctrlp

    # We know empirically that this generates tty messages
    ctrlp.play_start(controller=0xffffffff)
    ctrlp.play_data([0x10000]*8)  # PS button
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

    assert msgcount

    res = netmp.unregister(Ctrlp)
    assert res
    assert(res['result'] == 0)
    res = netmp.unregister(Ttyp)
    assert res
    assert(res['result'] == 0)

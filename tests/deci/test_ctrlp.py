#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import time

from skynet.deci.deci4 import Ctrlp


def test_basics(netmp):
    ctrlp = netmp.register(Ctrlp)
    assert ctrlp
    assert(type(ctrlp) == Ctrlp)

    res = ctrlp.get_conf()
    assert res
    assert (res['result'] == 0)

    # can't really test that keys worked right now
    res = ctrlp.play_start(controller=0)
    assert res
    assert(res['result'] == 0)

    res = ctrlp.play_data([0x10000]*8)  # PS button
    assert res
    assert(res['result'] == 0)

    res = ctrlp.play_data([0x0]*8)
    assert res
    assert(res['result'] == 0)

    res = ctrlp.play_stop()
    assert res
    assert(res['result'] == 0)

    res = ctrlp.rec_start(controller=0)
    assert res
    assert(res['result'] == 0)

    time.sleep(0.1)

    res = ctrlp.rec_stop()
    assert res
    assert(res['result'] == 0)

    cnt = 0
    while True:
        block = ctrlp.read_raw_data()
        if not block:
            break
        assert(type(block) == bytes)
        cnt += 1

    # If controller not on, will be zero
    # assert(cnt > 0)

    res = netmp.unregister(Ctrlp)
    assert res
    assert(res['result'] == 0)

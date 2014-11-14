#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest

from skynet.deci import Netmp
from skynet.deci.deci4 import Tsmp, Ttyp, Ctrlp, NetmpProt


def test_basics(pytestconfig):
    netmp = Netmp(ip=pytestconfig.target_ip)

    res = netmp.connect()
    assert res
    assert(res['result'] == 0)

    res = netmp.get_conf()
    assert res
    assert(res['result'] == 0)
    assert(res['protocol'] == netmp.prot.PROTOCOL)
    assert(res['protocol'] == NetmpProt.PROTOCOL)

    tsmp = netmp.register(Tsmp)
    assert tsmp
    assert(type(tsmp) == Tsmp)

    res = netmp.get_registered_list()
    assert res
    assert (res['result'] == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 1)

    tsmp2 = netmp.register(Tsmp)
    assert tsmp2
    assert (type(tsmp2) == Tsmp)
    assert (tsmp2 is tsmp)

    res = netmp.get_registered_list()
    assert res
    assert (res['result'] == 0)
    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 1)

    ctrlp = netmp.register(Ctrlp)
    assert ctrlp
    assert (type(ctrlp) == Ctrlp)

    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 1)

    ttyp = netmp.register(Ttyp)
    assert ttyp
    assert (type(ttyp) == Ttyp)

    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ttyp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 1)

    res = netmp.unregister(Tsmp)
    assert (res is None)
    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ttyp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 1)

    res = netmp.unregister(Tsmp)
    assert res
    assert (res['result'] == 0)
    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ttyp.prot.PROTOCOL]) == 1)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 1)

    netmp.unregister(Ttyp)

    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ttyp.prot.PROTOCOL]) == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 1)

    assert res
    assert (res['result'] == 0)
    netmp.unregister(Ctrlp)

    res = netmp.get_registered_list()
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ttyp.prot.PROTOCOL]) == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == tsmp.prot.PROTOCOL]) == 0)
    assert (len([x for x in res['data'] if
                 netmp.client_id.startswith(x['owner']) and x['protocol'] == ctrlp.prot.PROTOCOL]) == 0)

    assert res
    assert(res['result'] == 0)

    res = netmp.disconnect()
    assert res
    assert(res['result'] == 0)


def test_nonmulti(pytestconfig):
    netmp = Netmp(ip=pytestconfig.target_ip)
    netmp.connect()

    netmp2 = Netmp(ip=pytestconfig.target_ip)
    netmp2.connect()

    tsmp = netmp.register(Tsmp)
    tsmp2 = netmp2.register(Tsmp)
    assert(tsmp2 is not tsmp)

    ttyp = netmp.register(Ttyp)
    ttyp2 = netmp2.register(Ttyp)
    assert(ttyp2 is not ttyp)

    res = netmp.disconnect()
    assert res
    assert(res['result'] == 0)

    res = netmp2.disconnect()
    assert res
    assert(res['result'] == 0)


def test_multi(pytestconfig):
    netmp = Netmp(ip=pytestconfig.target_ip)
    netmp.connect()

    res = netmp.get_owner()
    assert(res is None)

    netmp2 = Netmp(ip=pytestconfig.target_ip)
    netmp2.connect()

    netmp.register(Ctrlp)

    res = netmp.get_registered_list()
    assert res
    assert(res['result'] == 0)

    # for some reason, cannot set owner to fixed value
    res = netmp.get_owner()
    assert res
    assert(type(res) == str)

    res2 = netmp.get_owner()
    assert res2
    assert(type(res2) == str)
    assert(res == res2)

    with pytest.raises(Netmp.InUseException):
        netmp2.register(Ctrlp)

    res = netmp2.force_disconnect()
    assert res
    assert(res['result'] == 0)
    ctrlp2 = netmp2.register(Ctrlp)
    assert ctrlp2

    with pytest.raises(Netmp.InUseException):
        netmp.disconnect()

    assert(not netmp.is_connected())

    note = netmp.get_notification()
    assert(note['protocol'] == NetmpProt.PROTOCOL)
    assert(note['msgtype'] == NetmpProt.FORCE_DISCON_NOTIFICATION)

    res = netmp2.disconnect()
    assert res
    assert(res['result'] == 0)


def test_error():
    with pytest.raises(Exception):
        Netmp(ip="256.127.127.127")

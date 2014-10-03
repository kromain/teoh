#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest

from skynet import PSTarget, PSTargetInUseException, PSTargetUnreachableException
from skynet.deci import Netmp
import conftest

@pytest.fixture(scope="function")
def local_pstarget(request):
    target = PSTarget(conftest.target_ip)
    request.addfinalizer(target.disconnect)

    return target


def test_target_with_psdriver(local_pstarget):
    assert local_pstarget.dualshock is not None
    assert local_pstarget.osk is not None
    assert local_pstarget.console is not None
    assert local_pstarget.psdriver is not None


@pytest.mark.xfail
def test_target_without_psdriver(local_pstarget):
    # FIXME figure out a way to turn off the inspector server on the target
    assert local_pstarget.dualshock is not None
    assert local_pstarget.osk is not None
    assert local_pstarget.console is not None
    assert local_pstarget.psdriver is None


def test_target_disconnect(local_pstarget):
    local_pstarget.disconnect()

    assert local_pstarget.dualshock is None
    assert local_pstarget.osk is None
    assert local_pstarget.console is None
    assert local_pstarget.psdriver is None


def test_invalid_target_ip():
    with pytest.raises(PSTargetUnreachableException):
        target = PSTarget("0.0.0.0")
        target.disconnect()


def test_target_in_use():
    # Create a raw CTRLP connection to the target so the PSTarget below will fail with PSTargetInUseException
    try:
        netmp = Netmp(conftest.target_ip)
    except Exception:
        raise pytest.skip("target {} unavailable".format(conftest.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register_ctrlp()
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    with pytest.raises(PSTargetInUseException):
        target = PSTarget(conftest.target_ip)
        target.disconnect()

    # Netmp cleanup
    if ctrlp_registered:
        netmp.unregister_ctrlp()
    netmp.disconnect()


def test_target_force_connect():
    # Create a raw CTRLP connection to the target to simulate an existing connection
    try:
        netmp = Netmp(conftest.target_ip)
    except Exception:
        raise pytest.skip("target {} unavailable".format(conftest.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register_ctrlp()
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    target = PSTarget(conftest.target_ip, True)

    assert target.dualshock is not None

    target.disconnect()

    # Netmp cleanup
    if ctrlp_registered:
        netmp.unregister_ctrlp()
    netmp.disconnect()

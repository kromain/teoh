#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import pytest
import time

from skynet import PSTarget, PowerState, PSTargetInUseException, PSTargetUnreachableException
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


def test_info_functions(local_pstarget):
    # unfortunately, returns the email address, while is_user_signed_in expects the username
    # signin_id = local_pstarget.psdriver.execute_script("return sce.getSigninId()")
    # FIXME figure out a way to retrieve the current username
    assert not local_pstarget.is_user_signed_in("unknown_username")

    imgfile = "test_screenshot.jpg"
    local_pstarget.save_screenshot(imgfile)
    assert os.stat(imgfile)
    os.remove(imgfile)

    # is_user_signed_in and save_screenshot should still work in disconnected state
    local_pstarget.disconnect()

    assert not local_pstarget.is_user_signed_in("unknown_username")

    imgfile = "test_screenshot.jpg"
    local_pstarget.save_screenshot(imgfile)
    assert os.stat(imgfile)
    os.remove(imgfile)


def test_power_functions(local_pstarget):
    assert local_pstarget.power_state() == PowerState.VSH_READY

    # power functions should still work in disconnected state
    local_pstarget.disconnect()

    assert local_pstarget.power_state() == PowerState.VSH_READY

    # TEMP until DECI support is improved
    pytest.skip("continuous tracking of power_state() during reboot not working yet")

    local_pstarget.reboot()

    while local_pstarget.power_state() != PowerState.REBOOT_STARTED:
        print(local_pstarget.power_state())
        time.sleep(3)

    while local_pstarget.power_state() != PowerState.VSH_READY:
        print(local_pstarget.power_state())
        time.sleep(3)


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

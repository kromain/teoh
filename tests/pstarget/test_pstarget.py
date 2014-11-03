#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import pytest
import time

from skynet import PSTarget, DS, PowerState
from skynet import PSTargetInUseException, PSTargetUnreachableException, PSTargetWebViewUnavailableException
from skynet.deci import Netmp, Console, Info, Power
from skynet.deci.deci4 import Ctrlp

import conftest


@pytest.fixture(scope="function")
def local_pstarget(request):
    target = PSTarget(conftest.target_ip)
    request.addfinalizer(target.release)

    return target


@pytest.fixture(scope="function")
def connected_pstarget(local_pstarget):
    local_pstarget.connect()
    return local_pstarget


def test_disconnected_target(local_pstarget):
    assert local_pstarget.dualshock is None
    assert local_pstarget.osk is None
    assert local_pstarget.tty is not None
    assert local_pstarget.psdriver is not None


def test_connected_target(connected_pstarget):
    assert connected_pstarget.dualshock is not None
    assert connected_pstarget.osk is not None
    assert connected_pstarget.tty is not None
    assert connected_pstarget.psdriver is not None


@pytest.mark.xfail(reason="needs ShellUI logout/login routines to test on login screen then log back in")
def test_target_without_psdriver(local_pstarget):
    assert local_pstarget.tty is not None

    with pytest.raises(PSTargetWebViewUnavailableException):
        assert local_pstarget.psdriver is not None


def test_target_disconnect(connected_pstarget):
    connected_pstarget.disconnect()

    assert connected_pstarget.dualshock is None
    assert connected_pstarget.osk is None


def test_target_psdriver(local_pstarget):
    assert local_pstarget.psdriver is not None
    # System (Secure) webview is called Swordfish
    assert "Swordfish" in local_pstarget.psdriver.title

    # check that the psdriver object has been cleaned up
    local_pstarget.release()
    assert local_pstarget._psdriver is None


def test_target_tty(local_pstarget):
    # make sure the TTY object is initialized
    assert local_pstarget.tty is not None
    assert Console in local_pstarget._deci_wrappers

    # tty.read() should return immediately with None if there's no data
    msg = local_pstarget.tty.read()
    assert msg is None or len(msg) > 0

    # going in and out of What's New reliably generates TTY output
    local_pstarget.connect()
    local_pstarget.dualshock.press_buttons([DS.DOWN, DS.UP])
    msg = local_pstarget.tty.read()
    assert msg is not None and len(msg) > 0

    # check that the TTY object has been cleaned up
    local_pstarget.release()
    assert Console not in local_pstarget._deci_wrappers


def test_info_functions(local_pstarget):
    # unfortunately, returns the email address, while is_user_signed_in expects the username
    # signin_id = local_pstarget.psdriver.execute_script("return sce.getSigninId()")
    # FIXME figure out a way to retrieve the current username
    # PENDING currently disabled due to a bug in the deci layer (fix pending)
    # assert not local_pstarget.is_user_signed_in("unknown_username")

    imgfile = "test_screenshot.tga"
    local_pstarget.save_screenshot(imgfile)
    assert os.stat(imgfile)
    os.remove(imgfile)

    # check that the underlying Info object has been cleaned up
    local_pstarget.release()
    assert Info not in local_pstarget._deci_wrappers


def test_power_functions(local_pstarget):
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

    # check that the underlying Power object has been cleaned up
    local_pstarget.release()
    assert Power not in local_pstarget._deci_wrappers


def test_invalid_target_ip():
    target = PSTarget("0.0.0.0")

    with pytest.raises(PSTargetUnreachableException):
        target.connect()
    assert target.dualshock is None
    assert target.osk is None

    with pytest.raises(PSTargetUnreachableException):
        target.tty.read()
    assert Console not in target._deci_wrappers

    with pytest.raises(PSTargetUnreachableException):
        assert target.is_user_signed_in("foo")
    assert Info not in target._deci_wrappers

    with pytest.raises(PSTargetUnreachableException):
        target.reboot()
    assert Power not in target._deci_wrappers

    with pytest.raises(PSTargetUnreachableException):
        target.psdriver.refresh()
    assert target._psdriver is None


def test_target_in_use():
    # Create a raw CTRLP connection to the target so the PSTarget below will fail with PSTargetInUseException
    try:
        netmp = Netmp(conftest.target_ip)
    except Exception:
        pytest.skip("target {} unavailable".format(conftest.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register(Ctrlp)
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    target = PSTarget(conftest.target_ip)
    with pytest.raises(PSTargetInUseException):
        target.connect()
    target.release()

    # Netmp cleanup
    if ctrlp_registered:
        netmp.unregister(Ctrlp)
    netmp.disconnect()


@pytest.mark.skipif(True, reason="skipping due to Netmp multiple connection issue leading to hangs (fix pending)")
def test_target_force_connect():
    # Create a raw CTRLP connection to the target to simulate an existing connection
    try:
        netmp = Netmp(conftest.target_ip)
    except Exception:
        pytest.skip("target {} unavailable".format(conftest.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register(Ctrlp)
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    target = PSTarget(conftest.target_ip)
    target.connect(force=True)
    assert target.dualshock is not None
    target.release()

    # Netmp cleanup
    # the first CTRLP connection has been closed, so this should now throw an InUseException
    with pytest.raises(Netmp.InUseException):
        if ctrlp_registered:
            netmp.unregister(Ctrlp)
        netmp.disconnect()

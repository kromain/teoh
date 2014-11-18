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


def test_disconnected_target(disconnected_pstarget_function):
    pstarget = disconnected_pstarget_function
    
    assert pstarget.dualshock is None
    assert pstarget.osk is None
    assert pstarget.tty is not None
    assert pstarget.webview is not None


def test_connected_target(pstarget_function):
    pstarget = pstarget_function
    
    assert pstarget.dualshock is not None
    assert pstarget.osk is not None
    assert pstarget.tty is not None
    assert pstarget.webview is not None


@pytest.mark.xfail(reason="needs ShellUI logout/login routines to test on login screen then log back in")
def test_target_without_webview(pstarget_function):
    pstarget = pstarget_function
    
    assert pstarget.tty is not None

    with pytest.raises(PSTargetWebViewUnavailableException):
        assert pstarget.webview is not None


def test_target_disconnect(pstarget_function):
    pstarget = pstarget_function

    pstarget.disconnect()

    assert pstarget.dualshock is None
    assert pstarget.osk is None


def test_target_webview(disconnected_pstarget_function):
    pstarget = disconnected_pstarget_function
    
    assert pstarget.webview is not None
    # System (Secure) webview is called Swordfish
    assert "Swordfish" in pstarget.webview.title

    # check that the webview object has been cleaned up
    pstarget.release()
    assert pstarget._webview is None


def test_target_tty(disconnected_pstarget_function):
    pstarget = disconnected_pstarget_function

    # make sure the TTY object is initialized
    assert pstarget.tty is not None
    assert Console in pstarget._deci_wrappers

    # tty.read() should return immediately with None if there's no data
    msg = pstarget.tty.read()
    assert msg is None or len(msg) > 0

    # going in and out of What's New reliably generates TTY output
    pstarget.connect()
    pstarget.dualshock.press_buttons([DS.DOWN, DS.UP])
    msg = pstarget.tty.read()
    assert msg is not None and len(msg) > 0

    # check that the TTY object has been cleaned up
    pstarget.release()
    assert Console not in pstarget._deci_wrappers


def test_info_functions(disconnected_pstarget_function):
    pstarget = disconnected_pstarget_function

    # unfortunately, returns the email address, while is_user_signed_in expects the username
    # signin_id = pstarget.webview.execute_script("return sce.getSigninId()")
    # FIXME figure out a way to retrieve the current username
    assert not pstarget.is_user_signed_in("unknown_username")

    imgfile = "test_screenshot.tga"
    pstarget.save_screenshot(imgfile)
    assert os.stat(imgfile)
    os.remove(imgfile)

    # check that the underlying Info object has been cleaned up
    pstarget.release()
    assert Info not in pstarget._deci_wrappers


def test_power_functions(disconnected_pstarget_function):
    pstarget = disconnected_pstarget_function

    assert pstarget.power_state() == PowerState.VSH_READY

    # TEMP until DECI support is improved
    pytest.skip("continuous tracking of power_state() during reboot not working yet")

    pstarget.reboot()

    while pstarget.power_state() != PowerState.REBOOT_STARTED:
        print(pstarget.power_state())
        time.sleep(3)

    while pstarget.power_state() != PowerState.VSH_READY:
        print(pstarget.power_state())
        time.sleep(3)

    # check that the underlying Power object has been cleaned up
    pstarget.release()
    assert Power not in pstarget._deci_wrappers


def test_invalid_target_ip():
    with pytest.raises(PSTargetUnreachableException):
        PSTarget("0.0.0.0")


def test_target_in_use(pytestconfig):
    # Create a raw CTRLP connection to the target so the PSTarget below will fail with PSTargetInUseException
    try:
        netmp = Netmp(pytestconfig.target_ip)
    except Exception:
        pytest.skip("target {} unavailable".format(pytestconfig.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register(Ctrlp)
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    target = PSTarget(pytestconfig.target_ip)
    with pytest.raises(PSTargetInUseException):
        target.connect()
    target.release()

    # Netmp cleanup
    if ctrlp_registered:
        netmp.unregister(Ctrlp)
    netmp.disconnect()


def test_target_force_connect(pytestconfig):
    # Create a raw CTRLP connection to the target to simulate an existing connection
    try:
        netmp = Netmp(pytestconfig.target_ip)
    except Exception:
        pytest.skip("target {} unavailable".format(pytestconfig.target_ip))

    ctrlp_registered = False
    try:
        netmp.connect()
        netmp.register(Ctrlp)
    except Netmp.InUseException:
        # fine we're already in the in-use state, nothing else to do
        pass
    else:
        ctrlp_registered = True

    target = PSTarget(pytestconfig.target_ip)
    target.connect(force=True)
    assert target.dualshock is not None
    target.release()

    # Netmp cleanup
    # the first CTRLP connection has been closed, so this should now throw an InUseException
    with pytest.raises(Netmp.InUseException):
        if ctrlp_registered:
            netmp.unregister(Ctrlp)
        netmp.disconnect()

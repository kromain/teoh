#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
from _pytest.runner import skip
import pytest

from skynet import PSTarget, PSTargetInUseException, PSTargetUnreachableException


@pytest.fixture(scope="session")
def pstarget_session(request):
    return _init_pstarget(request)


@pytest.fixture(scope="module")
def pstarget_module(request):
    return _init_pstarget(request)


@pytest.fixture(scope="class")
def pstarget_class(request):
    return _init_pstarget(request)


@pytest.fixture(scope="function")
def pstarget_function(request):
    return _init_pstarget(request)


@pytest.fixture(scope="session")
def disconnected_pstarget_session(request):
    return _init_pstarget(request, False)


@pytest.fixture(scope="module")
def disconnected_pstarget_module(request):
    return _init_pstarget(request, False)


@pytest.fixture(scope="class")
def disconnected_pstarget_class(request):
    return _init_pstarget(request, False)


@pytest.fixture(scope="function")
def disconnected_pstarget_function(request):
    return _init_pstarget(request, False)


@pytest.fixture(scope="session")
def forced_pstarget_session(request):
    return _init_pstarget(request, force_connection=True)


@pytest.fixture(scope="module")
def forced_pstarget_module(request):
    return _init_pstarget(request, force_connection=True)


@pytest.fixture(scope="class")
def forced_pstarget_class(request):
    return _init_pstarget(request, force_connection=True)


@pytest.fixture(scope="function")
def forced_pstarget_function(request):
    return _init_pstarget(request, force_connection=True)


def _init_pstarget(request, connect_target=True, force_connection=False):
    _debug_log("$$$ _init_pstarget")
    if hasattr(request.config, "target_ip"):
        # when running tests through mantis-run
        target_ip = request.config.target_ip
    elif hasattr(request.config.option, "ip"):
        # when running tests through pytest with --ip option parsing in conftest.py
        target_ip = request.config.option.ip
    else:
        raise RuntimeError("Not using a supported test runner! Please use mantis-run or py.test with --ip option.")

    try:
        target = PSTarget(target_ip)
        if connect_target:
            target.connect(force_connection)
    except PSTargetInUseException:
        print("********* FATAL : Target {} in use! Aborting test session *********".format(target_ip))
        skip("aborted")
    except PSTargetUnreachableException:
        print("******* FATAL : Target {} unreachable! Aborting test session *******".format(target_ip))
        skip("aborted")

    def _pstarget_finalize():
        _debug_log("$$$ _pstarget_finalize")
        target.release()
    request.addfinalizer(_pstarget_finalize)
    return target


_debug = os.getenv("SKYNET_TEST_DEBUG", "")

def _debug_log(str):
    global _debug
    if _debug:
        print(str)

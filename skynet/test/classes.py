#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest

from .fixtures import _debug_log


class SkynetTestCase:
    target = None
    config = None

    _skip_tearDownClass = False

    @classmethod
    @pytest.fixture(autouse=True, scope="class")
    def _skynet_init(cls, pstarget_session, request):
        _debug_log("*** _skynettestcase_init")
        request.addfinalizer(cls._skynet_finalize)

        cls.target = pstarget_session
        # config.skynet will be set when running with mantis-run, but not when running with py.test
        if hasattr(request.config, "skynet"):
            cls.config = request.config.skynet

        try:
            cls.setUpClass()
        except Exception:
            cls._skip_tearDownClass = True
            raise

    @classmethod
    def _skynet_finalize(cls):
        _debug_log("*** _skynettestcase_finalize")
        if not cls._skip_tearDownClass:
            # will call the subclass override if any
            cls.tearDownClass()

        cls.target = None
        cls.config = None

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class PSTestCase(SkynetTestCase):
    pass


class TLXTestCase(SkynetTestCase):
    pass

#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest

from .fixtures import _debug_log


class SkynetTestCase:
    """
    Base class for Skynet test cases

    This class provides a pair of :class:`~skynet.pstarget.PSTarget` and :class:`~skynet.config.config.Config` objects
    ready to use in tests, when grouping tests under a class. The target and config are automatically initialized
    before the first test starts, and automatically cleaned up after the last test finishes.

    You can define :meth:`setUpClass` and :meth:`tearDownClass` to add test-specific code that should be executed
    before the first test and after the last one, for example to go to a specific page or to start/stop an application.

    You can also define :meth:`setup_method` and :meth:`teardown_method` to add test-specific code that should be
    executed before and after each test method, for example to navigate to a specific page and back.

    Note that an alternative to using this class is to use the fixtures provided in :mod:`skynet.test.fixtures`.
    For more info on working with PyTest fixtures, see: http://pytest.org/latest/fixture.html
    """

    target = None
    """ The target on which the test is running. Automatically connected/disconnected before and after tests.

    :type: :class:`~skynet.pstarget.PSTarget`
    """
    config = None
    """ The Skynet config loaded from the shared and/or user config files for the test suite.

    :type: :class:`~skynet.config.config.Config`
    """

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
        """ Reimplement this method in your test class to add test-specific setup before the first test method starts
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """ Reimplement this method in your test class to add test-specific cleanup after the last test method finishes
        """
        pass


class PSTestCase(SkynetTestCase):
    """ Alias for :class:`SkynetTestCase`, for backwards compatibility with skynet-swordfish-tests
    """
    pass

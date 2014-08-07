#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
from skynet import PSTarget, PSTargetException, PSTargetInUseException, PSTargetUnreachableException
from skynet.deci import Netmp, Console
import conftest

test_target_ip = conftest.target_ip

class AvailablePSTargetTests(unittest.TestCase):
    def setUp(self):
        self.target = None
        try:
            self.target = PSTarget(test_target_ip)
        except PSTargetException:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

    def tearDown(self):
        if self.target:
            self.target.disconnect()

    def test_target_with_psdriver(self):
        self.assertIsNotNone(self.target.dualshock)
        self.assertIsNotNone(self.target.osk)
        self.assertIsNotNone(self.target.console)
        self.assertIsNotNone(self.target.psdriver)

    @unittest.expectedFailure
    def test_target_without_psdriver(self):
        # FIXME figure out a way to turn off the inspector server on the target
        self.assertIsNotNone(self.target.dualshock)
        self.assertIsNotNone(self.target.osk)
        self.assertIsNotNone(self.target.console)
        self.assertIsNone(self.target.psdriver)

    def test_target_disconnect(self):
        self.target.disconnect()

        self.assertIsNone(self.target.dualshock)
        self.assertIsNone(self.target.osk)
        self.assertIsNone(self.target.console)
        self.assertIsNone(self.target.psdriver)


class UnavailablePSTargetTests(unittest.TestCase):
    def test_invalid_target_ip(self):
        with self.assertRaises(PSTargetUnreachableException):
            target = PSTarget("0.0.0.0")
            target.disconnect()

    def test_target_in_use(self):
        # Create a raw CTRLP connection to the target so the PSTarget below will fail with PSTargetInUseException
        try:
            netmp = Netmp(test_target_ip)
        except Exception:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

        ctrlp_registered = False
        try:
            netmp.connect()
            netmp.register_ctrlp()
        except Netmp.InUseException:
            # fine we're already in the in-use state, nothing else to do
            pass
        else:
            ctrlp_registered = True

        with self.assertRaises(PSTargetInUseException):
            target = PSTarget(test_target_ip)
            target.disconnect()

        # Netmp cleanup
        if ctrlp_registered:
            netmp.unregister_ctrlp()
        netmp.disconnect()

    def test_target_force_connect(self):
        # Create a raw CTRLP connection to the target to simulate an existing connection
        try:
            netmp = Netmp(test_target_ip)
        except Exception:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

        ctrlp_registered = False
        try:
            netmp.connect()
            netmp.register_ctrlp()
        except Netmp.InUseException:
            # fine we're already in the in-use state, nothing else to do
            pass
        else:
            ctrlp_registered = True

        target = PSTarget(test_target_ip, True)

        self.assertIsNotNone(target.dualshock)

        target.disconnect()

        # Netmp cleanup
        with self.assertRaises(Exception):
            if ctrlp_registered:
                netmp.unregister_ctrlp()
            netmp.disconnect()


if __name__ == '__main__':
    unittest.main()

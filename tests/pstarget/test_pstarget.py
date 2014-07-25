#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import unittest
from skynet import PSTarget, PSTargetException, PSTargetInUseException, PSTargetUnreachableException
from skynet.deci import Netmp

# FIXME get a target IP from the config instead
test_target_ip = "43.138.14.26"


class PSTargetTest(unittest.TestCase):
    def test_invalid_target_ip(self):
        with self.assertRaises(PSTargetUnreachableException):
            target = PSTarget("0.0.0.0")
            target.disconnect()

    def test_target_with_psdriver(self):
        try:
            target = PSTarget(test_target_ip)
        except PSTargetException:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

        self.assertIsNotNone(target.dualshock)
        self.assertIsNotNone(target.osk)
        self.assertIsNotNone(target.psdriver)

        target.disconnect()

    @unittest.expectedFailure
    def test_target_without_psdriver(self):
        # FIXME figure out a way to turn off the inspector server on the target
        try:
            target = PSTarget(test_target_ip)
        except PSTargetException:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

        self.assertIsNotNone(target.dualshock)
        self.assertIsNotNone(target.osk)
        self.assertIsNone(target.psdriver)

        target.disconnect()

    def test_target_disconnect(self):
        try:
            target = PSTarget(test_target_ip)
        except PSTargetException:
            raise unittest.SkipTest("target {} unavailable".format(test_target_ip))

        target.disconnect()

        self.assertIsNone(target.dualshock)
        self.assertIsNone(target.osk)
        self.assertIsNone(target.psdriver)

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

        # cleanup
        if ctrlp_registered:
            netmp.unregister_ctrlp()
        netmp.disconnect()


if __name__ == '__main__':
    unittest.main()

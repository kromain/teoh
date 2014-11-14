#!/usr/bin/env python3
import os
import time
import pytest

from skynet.deci import Info
import conftest

test_target_ip = conftest.target_ip

class TestInfo:

    def setup(self):
        self.info = Info(test_target_ip)
        self.info.start()

    def teardown(self):
        self.info.stop()

    @pytest.mark.xfail
    def test_signedin(self):
        rc = self.info.is_user_signed_in("usersignedin")
        assert(rc)

    @pytest.mark.xfail
    def test_notsignedin(self):
        rc = self.info.is_user_signed_in("usersignedout")
        assert(rc)

    def test_nouser(self):
        rc = self.info.is_user_signed_in("usernotthere")
        assert(not rc)

    def test_info(self):
        infolist = self.info.get_info()


        assert(type(infolist) == dict)
        # Not sure I should test for what I observe the PS4 sending

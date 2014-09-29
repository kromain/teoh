#!/usr/bin/env python3
import os
import time
import pytest

from skynet.deci.info import Info
import conftest

test_target_ip = conftest.target_ip

class TestScreenshot:

    def setup(self):
        pass

    def teardown(self):
        pass


    def test_screenshot(self):
        with Info(ip=test_target_ip) as info:

            info.get_pict("TEST.tga")
            assert(os.path.getsize("TEST.tga") == 8294428)
            os.remove("TEST.tga")

            info.get_pict("TEST")
            assert(os.path.getsize("TEST.tga") == 8294428)
            os.remove("TEST.tga")
            
            info.get_pict("TEST.png")
            assert(os.stat("TEST.png"))
            with pytest.raises(FileNotFoundError):
                os.stat("TEST.tga")
            os.remove("TEST.png")

            assert(len([block for block in info.get_pict_blocks()]) == 127)






#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import pytest


pil_loaded = False
try:
    from PIL import Image
    pil_loaded = True
except:
    pass


def test_tga_screenshot(info):

    # just tests that the results are as big as we expect
    info.get_pict("TEST.tga")
    assert(os.path.getsize("TEST.tga") == 8294428)
    os.remove("TEST.tga")


def test_async_screenshot(info):
    # Async tests.  Try to do more than one call to TSMP protocol at the same time
    th1 = info.get_pict("ASYNC.tga", async=True)
    assert th1
    info.is_user_signed_in("steve-e1")
    th2 = info.get_pict("SYNC.tga", async=False)
    assert(not th2)
    assert(os.path.getsize("ASYNC.tga") == 8294428)
    th1.join()
    os.remove("ASYNC.tga")
    assert(os.path.getsize("SYNC.tga") == 8294428)
    os.remove("SYNC.tga")

    cnt = 0
    for block in info.get_pict_blocks():
        cnt += 1
        if cnt == 10:
            info.get_pict("TEST")

            assert(os.path.getsize("TEST.tga") == 8294428)
            os.remove("TEST.tga")

        if cnt == 127:
            assert(len(block) == 36892)
        else:
            assert(len(block) == 65536)

    assert(cnt == 127)


@pytest.mark.skipif(not pil_loaded, reason="requires Pillow package")
@pytest.mark.parametrize("extension", ["png", "jpg"])
def test_encoded_screenshot(info, extension):
    filename = "TEST.{}".format(extension)
    info.get_pict(filename)
    assert(os.stat(filename))
    with pytest.raises(FileNotFoundError):
        os.stat("TEST.tga")
    os.remove(filename)

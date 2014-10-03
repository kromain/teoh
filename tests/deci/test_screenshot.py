#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import pytest

from skynet.deci.info import Info
import conftest

pil_loaded = False
try:
    from PIL import Image
    pil_loaded = True
except:
    pass


@pytest.fixture(scope="module")
def info(request):
    i = Info(ip=conftest.target_ip)
    i.start()
    request.addfinalizer(i.stop)
    return i


def test_tga_screenshot(info):
    info.get_pict("TEST.tga")
    assert(os.path.getsize("TEST.tga") == 8294428)
    os.remove("TEST.tga")

    info.get_pict("TEST")
    assert(os.path.getsize("TEST.tga") == 8294428)
    os.remove("TEST.tga")

    assert len([block for block in info.get_pict_blocks()]) == 127


@pytest.mark.skipif(not pil_loaded, reason="requires Pillow package")
@pytest.mark.parametrize("extension", ["png", "jpg"])
def test_encoded_screenshot(info, extension):
    filename = "TEST.{}".format(extension)
    info.get_pict(filename)
    assert(os.stat(filename))
    with pytest.raises(FileNotFoundError):
        os.stat("TEST.tga")
    os.remove(filename)

#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import pytest


@pytest.mark.xfail
def test_signedin(info):
    rc = info.is_user_signed_in("usersignedin")
    assert rc


@pytest.mark.xfail
def test_notsignedin(info):
    rc = info.is_user_signed_in("usersignedout")
    assert rc


def test_nouser(info):
    rc = info.is_user_signed_in("usernotthere")
    assert not rc


def test_info(info):
    infolist = info.get_info()

    assert type(infolist) == dict
    # Not sure I should test for what I observe the PS4 sending

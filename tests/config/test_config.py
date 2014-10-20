#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#
# This is test for skynet.config 
 
import os
import pytest
import skynet

curr_dir = os.path.dirname(os.path.realpath(__file__))
skynet.Config.set_project_dir(curr_dir)

def test_default_json():
    assert len(skynet.Config().targets) == 2, "parser /skynet/skynet_config.json incorrectly"

def test_nonexist_json():
    with pytest.raises(FileNotFoundError):
        assert skynet.Config("/a/b/c.json").targets

def test_invalid_json_No_IP_Element():
    assert not skynet.Config(os.path.join(curr_dir,"invalid_no_IP.json")).targets

def test_invalid_json_No_ID_Element():
    config = skynet.Config(os.path.join(curr_dir,"invalid_no_ID.json"))
    assert len(config.targets) == 5
    assert config.targets[0].id == config.targets[0].ip

def test_invalid_json_format():
    with pytest.raises(skynet.InvalidConfigException):
        assert skynet.Config(os.path.join(curr_dir,"invalid_format_error.json")).targets

def test_invalid_IP():
    assert len(skynet.Config(os.path.join(curr_dir,"invalid_IP.json")).targets) == 1

def test_library_paths():
    config = skynet.Config()
    assert len(config.library_paths) == 1
    assert config.library_paths[0] == os.path.dirname(__file__)

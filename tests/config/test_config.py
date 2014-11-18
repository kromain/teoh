#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#

import os
import pytest
import sys

from skynet.config import Config, ConfigType, InvalidConfigError

curr_dir = os.path.dirname(__file__)
Config.set_project_dir(curr_dir)


def test_shared_config():
    conf = Config(ConfigType.SHARED)
    assert len(conf.targets) == 2
    target = conf.targets[0]
    assert target.ip == "172.31.1.27" and target.id == "PS4 DevKit Foo"
    target = conf.targets[1]
    assert target.ip == "172.31.1.28" and target.id == "PS4 DevKit Bla"
    assert len(conf.users) == 2
    user = conf.users[0]
    assert user.psnid == "user1" and user.email == "user1@email.com" and user.password == "abcd1234"
    user = conf.users[1]
    assert user.psnid == "user2" and user.email == "user2@email.com" and user.password == "dcba4321"
    assert len(conf.library_paths) == 1
    assert conf.library_paths[0] == curr_dir
    assert conf.test_data

test_retry = 5
def test_user_config():
    global test_retry
    test_retry -= 1
    conf = Config()
    assert len(conf.targets) == test_retry
    target = conf.targets[0]
    assert target.ip == "172.31.1.67" and target.id == "User PS4 DevKit"
    assert len(conf.users) == 1
    user = conf.users[0]
    assert user.psnid == "customuser" and user.email == "me@email.com" and user.password == "ps4rox"
    assert len(conf.library_paths) == 1
    assert conf.library_paths[0] == curr_dir
    assert conf.test_data


def test_custom_shared_config_basename():
    assert Config(ConfigType.SHARED, file_basename="myconfig", file_ext="json").targets


def test_custom_user_config_ext():
    assert Config(ConfigType.USER, user_ext="foo").targets


def test_user_config_without_shared_config():
    conf = Config(ConfigType.USER, file_basename="no_shared_config")
    assert len(conf.targets) == 1
    assert len(conf.library_paths) == 0


def test_user_config_without_user_config():
    with pytest.raises(FileNotFoundError) as e:
        Config(ConfigType.USER, file_basename="no_user_config")
    print("Caught expected exception:\n  {}".format(e))

def test_unknown_shared_config():
    with pytest.raises(FileNotFoundError) as e:
        Config(ConfigType.SHARED, file_basename="foo")
    print("Caught expected exception:\n  {}".format(e))


def test_unknown_user_config():
    with pytest.raises(FileNotFoundError) as e:
        Config(ConfigType.USER, user_ext="bar")
    print("Caught expected exception:\n  {}".format(e))


def test_invalid_json_format():
    with pytest.raises(InvalidConfigError) as e:
        Config(ConfigType.SHARED, file_basename="invalid_format")
    print("Caught expected exception:\n  {}".format(e))


def test_missing_target_ip():
    assert not Config(ConfigType.SHARED, file_basename="missing_target_ip").targets


def test_missing_target_id():
    conf = Config(ConfigType.SHARED, file_basename="missing_target_id")
    assert len(conf.targets) == 3
    for target in conf.targets:
        assert target.id == target.ip


def test_invalid_target_ip():
    assert len(Config(ConfigType.SHARED, file_basename="invalid_target_ip").targets) == 1


def test_library_paths():
    config = Config(ConfigType.SHARED, file_basename="library_paths")
    assert len(config.library_paths) == 5

    assert config.library_paths[0] == curr_dir
    assert config.library_paths[1] == os.path.normpath(curr_dir + "/../../skynet")
    assert config.library_paths[2] == os.path.join(curr_dir, "libpath1")
    assert config.library_paths[3] == os.path.join(curr_dir, "libpath2")
    if sys.platform == 'win32':
        assert config.library_paths[4] == os.path.normpath("C:/Windows")
    else:
        assert config.library_paths[4] == os.path.normpath("/usr/local")


def test_test_data():
    conf = Config()
    d = conf.test_data

    assert "string_data" in d and d["string_data"] == "foobar"
    assert "list_data" in d and d["list_data"] == ["foo", "bar"]
    assert "object_data" in d

    obj = d["object_data"]
    assert "prop1" in obj and obj["prop1"] == "foo"
    assert "prop2" in obj and obj["prop2"] == "bar"




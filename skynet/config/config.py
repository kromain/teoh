#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
import json
import os
import socket

from enum import IntEnum
from glob import glob


class InvalidConfigError(Exception):
    """
    Represents a JSON format error in the skynet config file
    """
    pass

class ConfigType(IntEnum):
    """
    Represents the type of skynet config to load.

    Used by the :class:`Config` constructor.
    """
    USER = 0x0
    SHARED = 0x1


def _is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


class TargetConfig(object):
    """
    Represents the details of a target in the *targets* section of the config file.

    This class provides access to the following properties for each target in the config:

    * :attr:`ip`: the target IPv4 address
    * :attr:`id`: the associated target name, which defaults to the IP address if not specified in the config.

    Nb: this class is managed internally by the :class:`Config` class.
    """
    def __init__(self, target_ip, target_id):
        self._ip = target_ip
        self._id = target_id

    @property
    def ip(self):
        """ The target IPv4 address

        :type: String
        """
        return self._ip

    @property
    def id(self):
        """ The associated target name (defaults to the IP address if not specified in the config)

        :type: String
        """
        return self._id


class Config():
    """
    This class provides access to the contents of the Skynet configuration files.

    There are two types of configuration files loaded by Skynet for each test suite:

    * Shared config file (default: *skynet.conf*): this file contains global configuration settings, shared between
      all users. This typically includes a pool of targets and the library paths for the test suite. This file is
      usually part of the repository for the test suites, and gets checked out by all users when cloning the repo.
      This is also meant to be the config used by the CI system.
    * User config file (default: *skynet.user.conf*): this files contains user-specific settings, only applicable
      to the user development environment. This typically includes the user's own devkit settings (IP, username...).
      This file should never be checked in the test suite repository.

    The *config_type* constructor argument must be one of the values from the :class:`~skynet.config.config.ConfigType`
    enum. If it is set to :attr:`~skynet.config.config.ConfigType.SHARED` then only the shared config file is parsed,
    but if it is set to :attr:`~skynet.config.config.ConfigType.USER`, then *both* the shared and user config files are
    parsed. If either is missing, a :class:`FileNotFoundError` will be thrown.

    When both files are found and parsed, the settings defined in the user config file always take precedence over
    the shared settings. However shared settings not also defined in the user config file are not hidden. This allows
    customizing some settings like targets, while keeping project-wide defaults for others such as library paths.

    For example, if a shared config contains a *targets* section and a *library_paths* section, and the user config
    contains a *targets* section only, the resulting config will return the *targets* list from the user
    config, and it will return the *library_paths* list from the shared config.

    By default, project files are expected to be found in the current working directory. You can call the class method
    :meth:`set_project_dir` if you want to change the folder in which the files are located.

    :param config_type: the type of config. The default is :attr:`~skynet.config.config.ConfigType.USER`.
    :type config_type: :class:`~skynet.config.config.ConfigType`
    :param String user_ext: the name of the extra extension before .conf for user config files. The default is "user".
    :param String file_basename: the base name for both shared and user config files. The default is "skynet".
    :param String file_ext: the config file extension, for both shared and user config files. The default is "conf".
    """

    _project_dir = "."

    @classmethod
    def set_project_dir(cls, pdir):
        """ Sets the directory into which the shared and user config files are located.

        :param String pdir: the directory for the config files, can be a relative or absolute path.
        """
        cls._project_dir = pdir

    @classmethod
    def project_dir(cls):
        """ Returns the directory into which the shared and user config files are located.

        :return: the directory for the config files as an absolute path
        """
        return os.path.abspath(cls._project_dir)

    def __init__(self, config_type=ConfigType.USER, user_ext="user", file_basename="skynet", file_ext="conf"):
        self._targets = []
        self._library_paths = []
        self._test_data = {}

        shared_filename = "{}.{}".format(file_basename, file_ext)
        user_filename = "{}.{}.{}".format(file_basename, user_ext, file_ext)

        glob_matches = glob(os.path.join(self._project_dir, shared_filename))
        if not glob_matches:
            raise FileNotFoundError("Shared config file {} does not exist!"
                                    .format(os.path.join(self.project_dir(), shared_filename)))
        self._shared_conf_file = glob_matches.pop()
        self._parse_config_file(self._shared_conf_file)

        self._user_conf_file = None
        if config_type == ConfigType.USER:
            glob_matches = glob(os.path.join(self._project_dir, user_filename))
            if not glob_matches:
                raise FileNotFoundError("User config file {} does not exist!"
                                        .format(os.path.join(self.project_dir(), user_filename)))
            self._user_conf_file = glob_matches.pop()
            self._parse_config_file(self._user_conf_file)

    @property
    def targets(self):
        """ The list of valid targets parsed from either the shared or the user config file.

        Config *targets* entries with missing or invalid IP addresses will not be included in this list.

        :return: a list of :class:`TargetConfig` objects
        """
        return self._targets

    @property
    def library_paths(self):
        """ The list of valid library paths parsed from either the shared or the user config file.

        Config *library_path* entries which don't map to existing folders will not be included in this list.

        :return: a list of String objects representing absolute paths
        """
        return self._library_paths

    def _parse_config_file(self, file_path):
        with open(file_path) as json_data:
            try:
                data = json.load(json_data)
            except ValueError:
                raise InvalidConfigError(file_path + " format is incorrect!")
            else:
                self._parse_targets(data)
                self._parse_library_paths(data)

    def _parse_targets(self, data):
        if "targets" not in data:
            return

        self._targets = []
        for i in data["targets"]:
            try:
                target_ip = i["IP"].strip()
            except:
                print("Target config is missing required attribute 'IP'! Skipping.")
                continue
            if not _is_valid_ipv4_address(target_ip):
                print("Target config has invalid 'IP' attribute value '{}'! Skipping.".format(target_ip))
                continue
            try:
                target_id = i["ID"].strip()
            except:
                target_id = target_ip

            self._targets.append(TargetConfig(target_ip, target_id))

    def _parse_library_paths(self, data):
        if "library_paths" not in data:
            return

        self._library_paths = []
        for path in data["library_paths"]:
            glob_matches = glob(os.path.join(self._project_dir, path))
            for match in glob_matches:
                if not os.path.isdir(match):
                    print("library_path {} isn't a valid directory! Skipping.".format(match))
                    continue
                self._library_paths.append(os.path.normpath(match))

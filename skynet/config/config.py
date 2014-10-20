#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
# parser skynet ORBIS configuration Json file
# JSON format [ { "ID":"001", "IP":"1.2.3.4" }, { "ID":"002", "IP":"1.2.3.5" } ]
import json
import os
import socket


class InvalidConfigException(Exception):
    pass


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
    #class contains Target_ID and Target_IP
    def __init__(self, target_ip, target_id):
        self.ip = target_ip
        self.id = target_id


class Config():

    _project_dir = "."

    @classmethod
    def set_project_dir(cls, pdir):
        cls._project_dir = pdir

    @classmethod
    def project_dir(cls):
        return os.path.abspath(cls._project_dir)

    def __init__(self, file_path=None):
        if file_path is not None:
            self.json_loc = os.path.join(file_path)
        else:
            self.json_loc = os.path.join(self._project_dir, "skynet.conf")
        if not os.path.isfile(self.json_loc):
            raise FileNotFoundError("FILE: " + str(self.json_loc) + " does not exist!")

        self._targets = None
        self._library_paths = None

        # return target_config object list

    @property
    def targets(self):
        if self._targets is None:
            self.parse_json()
        return self._targets

    @property
    def library_paths(self):
        if self._library_paths is None:
            self.parse_json()
        return self._library_paths

    # get IP_addr stored in conf file. Append target_config object to list     
    def parse_json(self):
        with open(self.json_loc) as json_data:
            try:
                data = json.load(json_data)
            except ValueError:
                raise InvalidConfigException(self.json_loc + " format is incorrect!")
            else:
                self.parse_targets(data)
                self.parse_library_paths(data)

    def parse_targets(self, data):
        self._targets = []
        if "targets" not in data:
            return

        for i in data["targets"]:
            target_ip = ""
            target_id = ""
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

    def parse_library_paths(self, data):
        self._library_paths = []
        if "library_paths" not in data:
            return

        for path in data["library_paths"]:
            self._library_paths.append(path)


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
    #param: String file_loc: the config_Json file location, e.g. "/Users/Skynet/config/skynet.config"
    #if file_loc isn't specified, it will point to skynet_root/skynet.conf
    #return: getIP() will return a list containing all Orbis IP_addr 
    def __init__(self, file_loc=None):
        if file_loc is not None:
            self.json_loc = os.path.join(file_loc)
        else:
            
            self.root_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                          os.pardir, os.pardir)))
            self.json_loc = os.path.join(self.root_dir, "skynet.conf")
        if not os.path.isfile(self.json_loc):
            raise FileNotFoundError("FILE: " + str(self.json_loc) + " does not exist!")
        self.target_config_list = None
     
    # get IP_addr stored in conf file. Append target_config object to list     
    def parse_json(self):
        with open(self.json_loc) as json_data:
            try:
                data = json.load(json_data)
                target_data = data["targets"]
            except:
                raise InvalidConfigException(self.json_loc + " format is incorrect!")
            self.target_config_list = []
            for i in target_data:
                target_ip = ""
                target_id = ""
                try:
                    target_ip = i["IP"].strip()
                except:
                    print("Warning! Didn't find the Target IP!")
                    continue
                try:
                    target_id = i["ID"].strip()
                except:
                    print("Warning! Didn't find the Target ID!")
                    continue
                if _is_valid_ipv4_address(target_ip) and target_id.isdigit():
                    self.target_config_list.append(TargetConfig(target_ip, target_id))

    # return target_config object list  
    def target_configs(self):
        if self.target_config_list is None:
            self.parse_json()
        return self.target_config_list

#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import sys
import subprocess

from selenium import webdriver
from signal import SIGTERM, CTRL_C_EVENT
from subprocess import CalledProcessError, TimeoutExpired

class PSDriverError(Exception):
    pass

def _iswindows():
    return sys.platform == 'win32'

def _psdrivername():
    exename = 'psdriver'
    if _iswindows():
        exename += '.exe'
    return exename

def _psdriverpath():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'bin',
                        _psdrivername())

def _psdriverpid():
    # NOTE Assume no more than one psdriver instance running for now
    try:
        if _iswindows():
            stdout = subprocess.check_output(['tasklist.exe',
                                              '/NH', # no table headers
                                              '/FI', 'IMAGENAME eq {}'.format(_psdrivername())],
                                             universal_newlines=True).strip()
            commandname, sep, stdout = stdout.partition(' ')
            # tasklist.exe prints a message and returns errorcode 0 even when no files are matched,
            # otherwise the command is first token in the line
            if commandname != _psdrivername():
                raise CalledProcessError(1, '')
        else:
            stdout = subprocess.check_output(['ps',
                                              '--no-headers',
                                              '-C', _psdrivername()]).strip()

        # PID is the 1st token on the line on Unix and the 2nd on Windows
        # (1st token on Windows is the command itself, already removed above)
        pid, sep, stdout = stdout.partition(' ')
        return pid

    except CalledProcessError:
        # Non-zero return code means process not running
        return None
    except OSError:
        # This really shouldn't happen unless we're running on an OS from Outer Space
        raise PSDriverError("Couldn't query OS for running processes. What OS are you running on?!")


class PSDriverServer(object):
    def __init__(self):
        self.server_ip = None
        self.server_port = None


    def startLocalServer(self, server_port):
        if server_port is None:
            return False
        if _psdriverpid() is None:
            try:
                p = subprocess.Popen([_psdriverpath(),
                                      '--port={}'.format(server_port)],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
                # Wait up to 100ms to detect early process exit due to e.g. unavailable port
                p.wait(0.1)
                # TODO should we retry with the next port maybe?
                errormsg = "Fatal error during psdriver server startup: " + p.stdout
                raise PSDriverError(errormsg)
            except TimeoutExpired:
                # All good, this means the server is up and running
                pass
            except OSError as e:
                errormsg = "Couldn't execute {}!".format(_psdriverpath())
                raise PSDriverError(errormsg) from e
        else:
            # TODO currently assumes that the running server listens on server_port,
            # which may not always be the case. We may also have many servers on multiple ports.
            # So we should check the ports that are actually used by the running servers
            # and start a new instance on server_port if it wasn't bound to any server.
            pass

        self.server_ip = '127.0.0.1'
        self.server_port = server_port
        return True


    def stopLocalServer(self):
        pid = _psdriverpid()
        if pid is None:
            return False
        os.kill(pid, CTRL_C_EVENT if _iswindows() else SIGTERM)
        return True


    def restartLocalServer(self, server_port=None):
        if server_port is None:
            server_port = self.server_port
        self.stopServer()
        self.startServer(server_port)


    def connect(self, target_ip, target_port):
        if self.server_ip is None or self.server_port is None:
            return None
        chromeDriverOptions = {'debuggerAddress': "{}:{}".format(target_ip, target_port)}
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['chromeOptions'] = chromeDriverOptions

        # may throw a WebDriverException if connection fails
        driver = webdriver.Remote("http://{}:{}".format(self.server_ip, self.server_port), capabilities)
        # connection was successful, update target_ip and target_port
        self.target_ip = target_ip
        self.target_port = target_port

        return driver

# PENDING this should eventually be loaded from a config file or online params
server = PSDriverServer()
#if config.useLocalPSDriverServer:
server.startLocalServer(9515)

def connectToTarget(target_ip, target_port=860):
    return server.connect(target_ip, target_port)
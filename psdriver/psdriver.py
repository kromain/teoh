#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
import signal
import sys

from selenium import webdriver

def _iswindows():
    return sys.platform == 'win32'

class PSDriverError(Exception):
    pass

class PSDriverServer(object):
    def __init__(self):
        self.server_ip = None
        self.server_port = None

    def executable_name(self):
        exename = 'psdriver'
        if _iswindows():
            exename += '.exe'
        return exename

    def executable_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'bin',
                            self.executable_name())

    def pid(self):
        # NOTE Assume no more than one psdriver instance running for now
        try:
            if _iswindows():
                stdout = subprocess.check_output(['tasklist.exe',
                                                  '/NH', # no table headers
                                                  '/FI', 'IMAGENAME eq ' + self.executable_name()],
                                                 universal_newlines=True)
                commandname, sep, stdout = stdout.lstrip().partition(' ')
                # tasklist.exe returns 0 with an info message even when no files are matched,
                # otherwise the command is first token in the line
                if commandname != self.executable_name():
                    raise CalledProcessError(1, '')
            else:
                stdout = subprocess.check_output(['pgrep', '-l', self.executable_name()],
                                                 universal_newlines=True)
        except CalledProcessError:
            # Non-zero return code means process not running
            return None
        except OSError:
            # This really shouldn't happen unless we're running on an OS from Outer Space
            raise PSDriverError("Couldn't query OS for running processes. What OS is this?!")
        # PID is the 1st token on the line on Unix and the 2nd on Windows
        # (1st token on Windows is the command itself, already removed above)
        pid, sep, stdout = stdout.lstrip().partition(' ')
        return pid

    def start_local_server(self, server_port):
        if server_port is None:
            return False
        if self.pid() is None:
            try:
                p = subprocess.Popen([self.executable_path(),
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
                errormsg = "Couldn't execute {}!".format(self.executable_path())
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


    def stop_local_server(self):
        pid = self.pid()
        if pid is None:
            return False
        if _iswindows():
            os.kill(pid, signal.CTRL_C_EVENT)
        else:
            os.kill(pid, signal.SIGTERM)
        return True


    def restart_local_server(self, server_port=None):
        if server_port is None:
            server_port = self.server_port
        self.stop_local_server()
        self.start_local_server(server_port)


    def connect(self, target_ip, target_port=860):
        if self.server_ip is None or self.server_port is None:
            return None
        chromeDriverOptions = {'debuggerAddress': "{}:{}".format(target_ip, target_port)}
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['chromeOptions'] = chromeDriverOptions

        # may throw a WebDriverException if connection fails
        driver = webdriver.Remote("http://{}:{}".format(self.server_ip, self.server_port),
                                  capabilities)
        # connection was successful, update target_ip and target_port
        self.target_ip = target_ip
        self.target_port = target_port

        return driver

# PENDING this should eventually be loaded from a config file or online params
server = PSDriverServer()
#if config.useLocalPSDriverServer:
server.start_local_server(9515)

#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import os
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
import signal
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def _iswindows():
    return sys.platform == 'win32'


class PSDriverError(Exception):
    """
    Represents an error during startup of the PSDriver server
    """
    pass

class PSDriverConnectionError(Exception):
    """
    Represents an error when trying to connect to a target
    """
    pass

class PSDriverServer(object):
    """
    The backend PSDriver server that handles WebDriver connections to the remote targets
    """
    def __init__(self):
        self.server_ip = None
        self.server_port = None
        self.target_ip = None
        self.target_port = None
        self.server_handle = None

    @staticmethod
    def executable_name():
        """
        :return: The platform-specific server executable name (ie. with '.exe' on Windows)
        :rtype: String
        """
        exename = 'psdriver'
        if _iswindows():
            exename += '.exe'
        return exename

    def executable_path(self):
        """
        :return: The full path on disk of the server executable
        """
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'bin',
                            sys.platform,
                            self.executable_name())

    def pid(self):
        """
        Check if the psdriver server is running and return its pid.

        :note: We assume no more than one psdriver server instance running for now

        :return: The platform-specific executable pid as an integer, or None if not running yet
        :raises PSDriverError: if the pid couldn't be queried from the OS
        """
        try:
            if _iswindows():
                stdout = subprocess.check_output(['tasklist.exe',
                                                  '/NH',  # no table headers
                                                  '/FI', 'IMAGENAME eq ' + self.executable_name()],
                                                 universal_newlines=True)
                # noinspection PyTypeChecker
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
        # noinspection PyTypeChecker
        pid, sep, stdout = stdout.lstrip().partition(' ')
        return int(pid)

    def start_local_server(self, server_port):
        """
        Start the psdriver server on *server_port*, or do nothing if there's already a server running on that port.

        :param int server_port: the listening TCP port for the server
        :return: True if we started our internal server, or False if an external server is already running
        :raises PSDriverError: if the server couldn't be started, for example if *server_port* is invalid or in use
        """
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
                errormsg = "Fatal error during psdriver server startup: " + p.stdout.read().decode('latin1')
                raise PSDriverError(errormsg)
            except TimeoutExpired:
                # All good, this means the server is up and running
                self.server_handle = p
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
        return self.server_handle is not None

    def stop_local_server(self, stop_external_server=False):
        """
        Stop the psdriver server if running, do nothing otherwise.
        By default, only internal servers are stopped, this can be changed by setting *stop_external_server* to True.

        :param bool stop_external_server: if True, also stop external running servers. False by default.
        :return: True if the server was stopped, False otherwise (ie. internal server not started)
        """
        if self.server_handle is not None:
            # Only terminate the subprocess if it's still alive
            if self.server_handle.returncode is None:
                self.server_handle.terminate()
            self.server_handle = None
            return True

        if stop_external_server:
            external_pid = self.pid()
            if external_pid is not None:
                if _iswindows():
                    os.kill(external_pid, signal.CTRL_C_EVENT)
                else:
                    os.kill(external_pid, signal.SIGTERM)
                return True

        return False





    def restart_local_server(self, server_port=None):
        """
        Restart an internal psdriver server on *server_port*. If it's not already running, just start it.
        This method always stops external servers if one is running.

        :param int server_port: the listening TCP port for the server
        :raises PSDriverError: if the server couldn't be started, for example if *server_port* is already in use
        """
        if server_port is None:
            server_port = self.server_port
        self.stop_local_server(stop_external_server=True)
        self.start_local_server(server_port)

    def connect(self, target_ip, target_port=860):
        """
        Create a WebDriver connection to the target at *target_ip*.

        :param String target_ip: the target's IP address
        :param int target_port: the target's inspector server listening port, by default 860
        :return: a :class:`selenium.webdriver.Remote` instance if the connection if successful,
            or None if the server isn't running
        :raises PSDriverConnectionError: if the connection to the target failed
        """
        server.start_local_server(9515)
        if self.server_ip is None or self.server_port is None:
            return None

        chromedriveroptions = {'debuggerAddress': "{}:{}".format(target_ip, target_port)}
        loggingoptions = {'browser': 'OFF'}
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        capabilities['chromeOptions'] = chromedriveroptions
        capabilities['loggingPrefs'] = loggingoptions

        try:
            driver = webdriver.Remote("http://{}:{}".format(self.server_ip, self.server_port),
                                      capabilities,
                                      keep_alive=True)
            # WORKAROUND for D3918, due to a bug in PSDriver (ChromeDriver), likely this:
            # https://code.google.com/p/chromedriver/issues/detail?id=402
            #
            # Sometimes PSDriver loses track of responses in the inspector protocol, causing it
            # to hang waiting for a response it missed. The timeout for such hangs has been set
            # to 10 minutes (!), causing our tests to hang forever.
            #
            # The following hack, combined with enabling 'connected' mode for HTTP with the keep_alive
            # option above, allows us to set a much smaller timeout on the HTTP connection side
            # so we'll abort the HTTP request after 10 seconds instead of 10 minutes.
            # This doesn't solve the ChromeDriver bug and tests may still fail, but at least this will
            # solve the hangs in our tests, so we'll detect such issues faster and won't hold CI.
            driver.command_executor._conn.timeout = 10.0
        except WebDriverException as e:
            raise PSDriverConnectionError("Connection to target failed") from e

        # connection was successful, update target_ip and target_port
        self.target_ip = target_ip
        self.target_port = target_port

        return driver

server = PSDriverServer()

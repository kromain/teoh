#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import sys

import skynet.deci as deci
import skynet.psdriver as psdriver
import skynet.osk as osk


class PSTargetException(Exception):
    """
    Base class for exceptions related to PSTarget
    """
    pass


class PSTargetUnreachableException(PSTargetException):
    """
    Represents a DECI connection failure when trying to connect to a target (PSDriver exceptions are allowed)
    """
    pass


class PSTargetInUseException(PSTargetException):
    """
    Represents a DECI 'target in use' error when trying to connect to a target without force-mode
    """
    pass


class PSTarget(object):
    """
    Handles the remote connection to a PlayStation target (DevKit/TestKit).

    The PSTarget class mainly exposes two objects to control the target remotely:

    * :attr:`dualshock`: allows emulating DualShock keys on the target
    * :attr:`psdriver` allows introspecting webviews and executing JavaScript code on the target

    The remote connection to *target_ip* is handled automatically:
    :meth:`connect` is called from the constructor, and :meth:`disconnect` from the destructor.

    You can also use the :class:`PSTarget` class with the 'with' operator, for example::

        with PSTarget("123.123.123.123") as target:
            print("Target WebView URL: " + target.psdriver.current_url)
        # target is automatically disconnected then destroyed at the end of the 'with' block above
        print("bla")

    :param String target_ip: the IP address of the target, e.g. "43.138.12.123"
    :param Bool force_connect: If set to True, will take precedence over existing connections on the target rather than
                                raising :class:`PSTargetInUseException`. Passed to :meth:`connect`. Default is False.

    :raises PSTargetInUseException: if the target connection failed due to being in use
    :raises PSTargetUnreachableException: if the target connection failed due to being unreachable
    """
    def __init__(self, target_ip, force_connect=False):
        self.target_ip = target_ip
        """The remote target IP address

        :type: String
        """
        self.psdriver = None
        """The Webview introspection interface

        :type: :class:`selenium.webdriver.Remote`
        """
        self.dualshock = None
        """The Dualshock emulator interface

        :type: :class:`skynet.deci.dualshock.DualShock`
        """
        self.console = None
        """The remote console interface

        :type: :class:`skynet.deci.console.Console`
        """
        self.osk = None
        # self.tty = None
        self.connect(force_connect)

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        # self.connect() is called in __init__() instead
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        # PENDING figure out if exceptions should be suppressed or not
        return False

    def connect(self, force=False):
        """
        Connects to the target at the IP address specified in the constructor.

        Initializes and connects the following members:
        * :attr:`dualshock`: always initialized
        * :attr:`osk`: always initialized
        * :attr:`console`: always initialized
        * :attr:`psdriver`: only initialized if a webview is currently available on the target

        Does nothing if the target is already connected and all members initialized.

        You normally don't need to call this method explicitely, as it is automatically called by the constructor.
        However, if the :attr:`psdriver` member couldn't be initialized at the time the PSTarget was created,
        you may call this method again to initialize :attr:`psdriver` once a webview is available on the target.

        :param Bool force: if set to True, will take precedence over existing connections on the target rather than
                            raising :class:`PSTargetInUseException`. Default is False.

        :raises PSTargetInUseException: if the target connection failed due to being in use
        :raises PSTargetUnreachableException: if the target connection failed due to being unreachable
        """
        if self.dualshock is None:
            ds = deci.DualShock(self.target_ip, force)
            try:
                ds.start()
            except deci.Netmp.InUseException as e:
                raise PSTargetInUseException("Target already in use") from e
            except Exception as e:
                raise PSTargetUnreachableException("Target unreachable") from e
            else:
                self.dualshock = ds

        if self.console is None:
            cs = deci.Console(self.target_ip)
            try:
                cs.start()
            except Exception as e:
                raise PSTargetUnreachableException("Target unreachable") from e
            else:
                self.console = cs

        if self.osk is None:
            self.osk = osk.OskEntry(self.dualshock)
        if self.psdriver is None:
            try:
                self.psdriver = psdriver.server.connect(self.target_ip)
            except psdriver.PSDriverError:
                # We may not always have a webview available (e.g. at the login screen after bootup),
                # in this case we leave the psdriver part uninitialized, relying only on the deci part
                pass
            except Exception as e:
                # we need to disconnect here since __del__() won't be called as the exception is propagated
                self.disconnect()
                raise psdriver.PSDriverError("Error during psdriver connection initialization") from e

    def disconnect(self):
        """
        Disconnects from the target at the IP address specified in the constructor.

        Disconnects then resets the following members to None:
        * :attr:`dualshock`
        * :attr:`osk`
        * :attr:`console`
        * :attr:`psdriver`

        Does nothing if the target is already disconnected.

        This method is automatically called when the PSTarget object is GC'd or at the end of a 'with' block,
        but you may still want to call it explicitely to ensure the target connection is released as soon as possible.
        """
        try:
            if self.dualshock is not None:
                self.dualshock.stop()
                self.dualshock = None
            if self.osk is not None:
                self.osk = None
            if self.console is not None:
                self.console.stop()
                self.console = None
            if self.psdriver is not None:
                self.psdriver.quit()
                self.psdriver = None
        finally:
            psdriver.server.stop_local_server()


def main():
    """
    Simple checks, and prints out important words

    :return: zero if Skynet started successfully, non-zero otherwise
    """
    print("[08/29/1997 02:14] Skynet becomes self-aware.")
    print("PSDriver server: {} (pid={})".format(psdriver.server.executable_path(),
                                                psdriver.server.pid()))
    print("PSDriver version: " + psdriver.__version__)
    if len(sys.argv) < 2:
        print("No Target IP address specified, exiting.")
        return 1

    print("Connecting to target at {}...".format(sys.argv[1]))
    with PSTarget(sys.argv[1]) as target:
        print("Target WebView URL: " + target.psdriver.current_url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

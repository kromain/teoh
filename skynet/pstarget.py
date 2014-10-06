#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import sys

import skynet.psdriver as psdriver
import skynet.osk as osk
from skynet.deci import DualShock, Console, Info, Power, Netmp


class PSTargetException(Exception):
    """
    Base class for exceptions related to PSTarget
    """
    pass


class PSTargetUnreachableException(PSTargetException):
    """
    Represents a DECI connection failure when trying to connect to a target
    """
    pass


class PSTargetInUseException(PSTargetException):
    """
    Represents a DECI 'target in use' error when trying to connect to a target without force-mode
    """
    pass

class PSTargetWebViewUnavailableException(PSTargetException):
    """
    Represents a PSDriver connection failure when trying to connect to a webview on the target
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
        self.dualshock = None
        """The Dualshock emulator interface

        :type: :class:`skynet.deci.dualshock.DualShock`
        """
        self.osk = None
        """The ShellUI On-Screen Keyboard interface

        :type: :class:`skynet.osk.OskEntry`
        """

        self._psdriver = None
        self._deci_wrappers = {}

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
            ds = DualShock(self.target_ip, force)
            try:
                ds.start()
            except Netmp.InUseException as e:
                raise PSTargetInUseException("Target already in use") from e
            except Exception as e:
                raise PSTargetUnreachableException("Target unreachable") from e
            else:
                self.dualshock = ds

        if self.osk is None:
            self.osk = osk.OskEntry(self.dualshock)

    def disconnect(self):
        """
        Disconnects from the target at the IP address specified in the constructor.

        Closes all the active DECI connections (DualShock, TTY, Power...) then resets the following members to None:
        * :attr:`dualshock`
        * :attr:`osk`
        * :attr:`psdriver`

        Does nothing if the target is already disconnected.

        This method is automatically called when the PSTarget object is GC'd or at the end of a 'with' block,
        but you may still want to call it explicitely to ensure the target connection is released as soon as possible.
        """
        for wrapper in self._deci_wrappers.values():
            wrapper.stop()
        self._deci_wrappers.clear()

        if self.dualshock is not None:
            self.dualshock.stop()
            self.dualshock = None
        if self.osk is not None:
            self.osk = None
        if self._psdriver is not None:
            self._psdriver.quit()
            self._psdriver = None

    @property
    def psdriver(self):
        """The Webview introspection interface

        :type: :class:`selenium.webdriver.Remote`
        """
        if self._psdriver is None:
            try:
                self._psdriver = psdriver.server.connect(self.target_ip)
            except psdriver.PSDriverError:
                # Report psdriver server startup errors
                raise
            except psdriver.PSDriverConnectionError as e:
                # We may not always have a webview available (e.g. at the login screen after bootup)
                raise PSTargetWebViewUnavailableException from e
        return self._psdriver

    @property
    def tty(self):
        """The TTY console interface

        This object can be accessed regardless of the connection state.

        :type: :class:`skynet.deci.console.Console`
        """
        return self._deci_wrapper(Console)

    def is_user_signed_in(self, username):
        """
        Returns PSN sign-in status for the specified *username* on the target.

        This method can be called regardless of the connection state.

        :param string username: the PSN username to check for signed-in status
        :returns: True if the username is signed in to PSN on the target, False otherwise
        """
        return self._info.is_user_signed_in(username)

    def power_state(self):
        """
        Returns the power state for the target, as a :class:`skynet.deci.power.PowerState` enum value

        This method can be called regardless of the connection state.

        :returns: The current power status for the target
        :rtype: :class:`skynet.deci.power.PowerState`
        """
        return self._power.power_state()

    def save_screenshot(self, filepath):
        """
        Takes a screenshot on the target and saves it locally as the file specified by *filepath*.

        *filepath* can include an absolute or relative path with the file name. If only a file name is specified,
        it is saved in the current working dir.

        The format of the saved image is automatically determined based on the file extension, for example specifying
        'image.png' will save the screenshot as a PNG image. Supported extensions are:
        * '.jpg': encoded as a JPEG image (high compression, lossy)
        * '.png': encoded as a PNG image (medium compression, non-lossy)
        * '.tga': encdoded as a TARGA image (non-compressed, non-lossy)

        If no extension is specified, images are saved as *.tga by default.

        This method can be called regardless of the connection state.

        :param string filepath: the saved image file path
        """
        self._info.get_pict(filepath)

    def reboot(self):
        """
        Triggers a reboot of the target.

        This method can be called regardless of the connection state.
        """
        self._power.reboot()

    def power_off(self):
        """
        Triggers a target shutdown.

        This method can be called regardless of the connection state.
        """
        self._power.power_off()

    def _deci_wrapper(self, wrapper_class):
        if wrapper_class not in self._deci_wrappers:
            wrapper = wrapper_class(self.target_ip)
            try:
                wrapper.start()
            except Exception as e:
                raise PSTargetUnreachableException("Target unreachable") from e
            else:
                self._deci_wrappers[wrapper_class] = wrapper
        return self._deci_wrappers[wrapper_class]

    @property
    def _info(self):
        return self._deci_wrapper(Info)

    @property
    def _power(self):
        return self._deci_wrapper(Power)


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

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

    In addition, the class provides access to many utility interfaces and methods, such as :attr:`osk` to control
    OSK typing, :attr:`tty` to read the target's TTY console output, or :meth:`save_screenshot` to save a screenshot
    of the target as a PNG/JPEG image file on the host machine.

    The remote connection to *target_ip* is handled automatically in most cases, with the exception of the
    :attr:`dualshock` and :attr:`osk` interfaces, which require an explicit and exclusive connection to the target
    before being initialized. :meth:`connect` creates the connection, and :meth:`disconnect` ends it. Other interfaces
    and methods can be called regardless of the target connection state.

    PSTarget objects manage many network connections to the target internally, and you're responsible for releasing
    these connections by calling the :meth:`release` method at the end of your target session.

    A typical PSTarget session looks like:

        target = PSTarget("123.123.123.123")
        print(target.tty.read())
        assert target.psdriver.title == "Some Title"
        # explicit connection required for target.dualshock
        assert target.dualshock is None
        target.connect()
        target.dualshock.press_button(DS.CROSS)
        target.psdriver.execute_script("window.origin.href")
        # calls target.disconnect() implicitly
        target.release()
        assert target.dualshock is None

    You can also use the :class:`PSTarget` class with the 'with' operator to automatically handle the connection
    to the target, for example:

        with PSTarget("123.123.123.123") as target:
            target.dualshock.press_button(DS.CROSS)
            print("Target WebView URL: " + target.psdriver.current_url)
        # target is automatically released then destroyed at the end of the 'with' block above
        print("bla")

    :param String target_ip: the IP address of the target, e.g. "43.138.12.123"

    :raises PSTargetInUseException: if the target connection failed due to being in use
    :raises PSTargetUnreachableException: if the target connection failed due to being unreachable
    """
    def __init__(self, target_ip):
        self.target_ip = target_ip
        """The remote target IP address

        :type: String
        """
        self.dualshock = None
        """The Dualshock emulator interface. Only valid when the target is in connected state.

        :type: :class:`skynet.deci.dualshock.DualShock`
        """
        self.osk = None
        """The ShellUI On-Screen Keyboard interface. Only valid when the target is in connected state.

        :type: :class:`skynet.osk.OskEntry`
        """

        self._psdriver = None
        self._deci_wrappers = {}

    def __del__(self):
        self.release()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def release(self):
        """
        Closes all PSDriver and DECI connections to the target at the IP address specified in the constructor.

        This method implicitly calls :method:`disconnect` first, if the target is in connected state.

        You should call this method at the end of your PSTarget session to ensure all resources and connections
        are properly closed and cleaned up.
        """
        self.disconnect()

        for wrapper in self._deci_wrappers.values():
            wrapper.stop()
        self._deci_wrappers.clear()

        if self._psdriver is not None:
            self._psdriver.quit()
            self._psdriver = None

    def is_connected(self):
        """
        Returns whether this PSTarget instance is connected to the target at :attr:`target_ip`
        :return: True if the target is in connected state, False otherwise
        """
        return self.dualshock is not None

    def connect(self, force=False):
        """
        Connects to the target at the IP address specified in the constructor.

        Using the DualShock and/or OSK interfaces requires an exclusive DECI connection to the target.
        This method tries to set up the connection, and if successful initializes :attr:`dualshock` and :attr:`osk`.

        Does nothing if the target is already in connected state, with :attr:`dualshock` and :attr:`osk` initialized.

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

        Closes the exclusive connection required by the DualShock and OSK interfaces,
        then resets :attr:`dualshock` and :attr:`osk` to None.

        Does nothing if the target is already in disconnected state.
        """
        if self.dualshock is not None:
            self.dualshock.stop()
            self.dualshock = None
        if self.osk is not None:
            self.osk = None

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

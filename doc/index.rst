.. skynet documentation master file, created by
   sphinx-quickstart on Tue Jul  8 15:33:37 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Skynet's documentation!
==================================

.. toctree::

    installation

.. toctree::
    :hidden:

    skynet.*

A Hello Skynet example
----------------------

Here's a very basic example of a Python3 script using the Skynet API:

.. code-block:: python

    from skynet import PSTarget, DS

    target = PSTarget("43.138.15.51")
    target.connect()

    print("Going to What's New feed...")
    target.dualshock.press_button(DS.DOWN)

    print("Taking screenshot...")
    target.save_screenshot("whatsnew.png")

    print("Navigating back up...")
    target.dualshock.press_button(DS.CIRCLE)

    print("Webview title: " + target.webview.title)
    # this line will appear in the inspector console for the webview
    target.webview.execute_script("console.log('Hello Skynet!')")

    target.release()

This example assumes that you have a PS4 devkit with a DEVLAN IP set to 43.138.15.55, with a user
logged in the console as well as PSN, so that the What's New feed is shown.

The script creates a connection to the devkit, connects a virtual DualShock4 controller, then goes down
the What's New feed, fetches a screenshot and saves it as a PNG file, then goes back up and prints out
the title for the current webview (that is, Swordfish).
Finally, it prints out a "Hello Skynet!" message on the webview console, which can be seen with the remote
inspector. The connection to the devkit is then closed before exiting the script.

General API usage
-----------------

The Skynet API is centered around the :class:`~skynet.pstarget.PSTarget` class, which provides the entry point
to most of the remote control and introspection features, based on the DEVLAN IP address of the devkit .

The various features are accessed through properties of the class. The main ones are:

* :attr:`~skynet.pstarget.PSTarget.dualshock`: allows emulating DualShock keys on the target
* :attr:`~skynet.pstarget.PSTarget.webview` allows introspecting webviews and executing JavaScript code on the target

In addition, the class provides access to many utility interfaces and methods, such as
:attr:`~skynet.pstarget.PSTarget.osk` to control typing with the ShellUI OSK,
:attr:`~skynet.pstarget.PSTarget.tty` to read the target's TTY console output, or
:meth:`~skynet.pstarget.PSTarget.save_screenshot` to save a screenshot of the target as a PNG/JPEG image file
on the host machine.

The remote connection to the devkit is handled automatically in most cases, with the exception of the
:attr:`~skynet.pstarget.PSTarget.dualshock` and :attr:`~skynet.pstarget.PSTarget.osk` interfaces, which require
an explicit and exclusive connection to the target before being initialized.
This is similar to the "available/connected" indicator displayed in PS4 Neighborhood.
:meth:`~skynet.pstarget.PSTarget.connect` creates the connection, and :meth:`~skynet.pstarget.PSTarget.disconnect`
ends it. Other interfaces and methods can be called regardless of the target connection state.

:class:`~skynet.pstarget.PSTarget` objects manage many network connections to the target internally, and you're
responsible for releasing these connections by calling the :meth:`~skynet.pstarget.PSTarget.release` method
at the end of your target session.

An overview of the complete skynet package contents, including details of the :class:`~skynet.pstarget.PSTarget` API
and its members, can be found below.

skynet package overview:
------------------------

.. rubric:: Classes

.. automodule:: skynet.pstarget

    .. autosummary::
        :toctree:
        :nosignatures:

        PSTarget

.. automodule:: skynet.deci.dualshock

    .. autosummary::
        :toctree:
        :nosignatures:

        DualShock

.. automodule:: skynet.deci.console

    .. autosummary::
        :toctree:
        :nosignatures:

        Console

.. automodule:: skynet.osk.osk

    .. autosummary::
        :toctree:
        :nosignatures:

        OskEntry

.. automodule:: skynet.config.config

    .. autosummary::
        :toctree:
        :nosignatures:

        Config

.. rubric:: Enums

.. automodule:: skynet

    .. autosummary::
        :toctree:

        Buttons
        DS
        PowerState

.. rubric:: Exceptions

.. automodule:: skynet.pstarget

    .. autosummary::
        PSTargetException
        PSTargetInUseException
        PSTargetUnreachableException
        PSTargetWebViewUnavailableException

.. automodule:: skynet.config.config

    .. autosummary::
        InvalidConfigException

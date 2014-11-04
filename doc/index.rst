.. skynet documentation master file, created by
   sphinx-quickstart on Tue Jul  8 15:33:37 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Skynet's documentation!
==================================

.. toctree::
    :hidden:

    skynet.*

skynet package:
---------------

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

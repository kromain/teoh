import os
import sys
import pytest

from mantis.configmanager import get_skynet_config


class MantisNode:
    def __init__(self):
        self._retryitem = None

    @pytest.mark.tryfirst
    def pytest_runtest_protocol(self, item, nextitem):
        # detect test retries which always come in pairs
        if item == nextitem and self._retryitem is None:
            self._retryitem = item
            return

        if self._retryitem is not None:
            retryitem = self._retryitem
            # self._retryitem must be reset every time so we can properly handle item sequences like:
            # ['0','0','0','0']
            # (which would represent a same test being retried 2 times in a row)
            self._retryitem = None

            if item == retryitem:
                # This is the duplicate retry item, discard it
                return True


# -------------------------------------------------------------------------
# distributed testing slave initialization
# -------------------------------------------------------------------------


def pytest_configure(config, __multicall__):
    __multicall__.execute()

    # extract the current target_ip and attach to config
    config.target_ip = os.getenv("SKYNET_TARGET_IP", "")

    conf = get_skynet_config(config)
    # Add any specified library paths to the Python system path
    if conf is not None and conf.library_paths:
        sys.path.extend(conf.library_paths)
    # attach to the pytest config object
    config.skynet = conf

    config.pluginmanager.register(MantisNode(), "mantisnode")

    # Consider all classes for tests (default is only classes that start with "Test")
    # (note that config.addinivalue_line() fails because python_classes doesn't return a list as expected)
    config._inicache["python_classes"] = [""]

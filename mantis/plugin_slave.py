import os
import sys
import types
import pytest

from mantis import configmanager
from skynet import psdriver


# Overrides xdist.remote.SlaveInteractor.pytest_runloop()
# to support running one test at a time
def mantis_runtestloop(self, session):
    self.log("entering main loop")
    torun = []
    while 1:
        name, kwargs = self.channel.receive()
        self.log("received command", name, kwargs)
        if name == "runtests":
            torun.extend(kwargs['indices'])
        elif name == "runtests_all":
            torun.extend(range(len(session.items)))
        self.log("items to run:", torun)
        # only run if we have an item and a next item
        while torun:
            self.run_tests(torun)
        if name == "shutdown":
            if torun:
                self.run_tests(torun)
            break
    return True

# -------------------------------------------------------------------------
# distributed testing slave initialization
# -------------------------------------------------------------------------


def pytest_configure(config, __multicall__):
    __multicall__.execute()

    # extract the current target_ip and attach to config
    config.target_ip = os.getenv("SKYNET_TARGET_IP", "")

    # check for external psdriver server setting
    psdriver_ip, psdriver_port = configmanager.parse_cmdline_psdriver(config)
    if psdriver_ip and psdriver_port:
        psdriver.server.use_external_server(psdriver_ip, psdriver_port)

    conf = configmanager.get_skynet_config(config)
    # Add any specified library paths to the Python system path
    if conf is not None and conf.library_paths:
        sys.path.extend(conf.library_paths)
    # attach to the pytest config object
    config.skynet = conf

    for plugin in config.pluginmanager.getplugins():
        if type(plugin).__name__ == "SlaveInteractor":
            plugin.pytest_runtestloop = types.MethodType(mantis_runtestloop, plugin)
            break

    # Consider all classes for tests (default is only classes that start with "Test")
    # (note that config.addinivalue_line() fails because python_classes doesn't return a list as expected)
    config._inicache["python_classes"] = [""]

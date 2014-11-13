import skynet
import sys

from mantis.configmanager import get_skynet_config

# -------------------------------------------------------------------------
# distributed testing slave initialization
# -------------------------------------------------------------------------

def pytest_configure(config, __multicall__):
    __multicall__.execute()

    conf = get_skynet_config(config)
    # Add any specified library paths to the Python system path
    if conf is not None and conf.library_paths:
        sys.path.extend(conf.library_paths)
    # attach to the pytest config object
    config.skynet = conf

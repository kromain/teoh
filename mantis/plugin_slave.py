import skynet
import sys

# -------------------------------------------------------------------------
# distributed testing slave initialization
# -------------------------------------------------------------------------

def pytest_configure(config, __multicall__):
    __multicall__.execute()

    # TODO
    # skynet.Config.set_project_dir()

    # Add any specified library paths to the Python system path
    try:
        sys.path.extend(skynet.Config().library_paths)
    except FileNotFoundError:
        pass

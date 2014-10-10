import os
import sys

import pytest
import _pytest.config
from skynet.config import Config


def extract_node_count(config):
    return str(len(config.target_configs()))


def main():
    args = sys.argv[1:]

    skynet_config = Config()
    skynet_config.parse_json()
    args.extend(["-n", extract_node_count(skynet_config)])
    args.extend(["--ip=1.2.3.4"])

    pluginmanager = _pytest.config.get_plugin_manager()
    try:
        config = pluginmanager.hook.pytest_cmdline_parse(pluginmanager=pluginmanager, args=args)
        exitstatus = pluginmanager.hook.pytest_cmdline_main(config=config)
    except pytest.UsageError:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" %(e.args[0],))
        exitstatus = -1
    return exitstatus

if __name__ == "__main__":
    main()

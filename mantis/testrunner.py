import os
import sys

import pytest
import _pytest.config


def testrunner_main():
    args = sys.argv[1:]

    args.extend(["-p", "mantis.pytest_plugin"])

    pluginmanager = _pytest.config.get_plugin_manager()
    try:
        config = pluginmanager.hook.pytest_cmdline_parse(pluginmanager=pluginmanager, args=args)
        exitstatus = pluginmanager.hook.pytest_cmdline_main(config=config)
    except pytest.UsageError:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" % (e.args[0],))
        exitstatus = -1
    return exitstatus


if __name__ == "__main__":
    main()
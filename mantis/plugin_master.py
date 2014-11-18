import pytest
import sys
from mantis import configmanager

from xdist.dsession import DSession, LoadScheduling
from xdist.slavemanage import NodeManager
from skynet.config.config import Config


class InvalidIpError(Exception):
    pass


def mantis_node_specs(targetconfig):
    return ["popen//id={} <{}>//env:SKYNET_TARGET_IP={}".format(tc.id, tc.ip, tc.ip)
            for tc in targetconfig]


def format_report_output(sections):
    if not sections:
        return

    print("")  # because test result indicators don't add a newline (so they can be combined e.g. "..E.s..")
    for section in sections:
        dest, content = section
        for line in content.split("\n"):
            if "stderr" in dest:
                print("! ", line, file=sys.stderr)
            else:
                print("> ", line, file=sys.stdout)


class MantisSession(DSession):
    def __init__(self, config):
        super().__init__(config)
        self._skynet_config = None

    @pytest.mark.trylast
    def pytest_sessionstart(self, session):
        """Creates and starts the nodes.

        The nodes are setup to put their events onto self.queue.  As
        soon as nodes start they will emit the slave_slaveready event.
        """

        # avoid infinite recursion by loading the plugin again in the spawned nodes
        self.config.option.plugins.remove("mantis.plugin_master")
        self.config.option.plugins.append("mantis.plugin_slave")

        # Command line args take precedence over config files
        cmdline_ips = configmanager.parse_cmdline_ip_list(self.config)
        cmdline_users = configmanager.parse_cmdline_users(self.config)

        self._skynet_config = configmanager.get_skynet_config(self.config)
        if self._skynet_config is None:
            print("*** NOTE: No Skynet user config file found in {}!".format(Config.project_dir()))
            print("      --> Creating 'skynet.user.conf' in folder using command arguments.")
            configmanager.create_user_config_file(cmdline_ips, cmdline_users)
            self._skynet_config = configmanager.get_skynet_config(self.config)

        node_specs = mantis_node_specs(cmdline_ips if cmdline_ips else self._skynet_config.targets)
        self.nodemanager = NodeManager(self.config, node_specs)
        nodes = self.nodemanager.setup_nodes(putevent=self.queue.put)
        self._active_nodes.update(nodes)

    def pytest_sessionfinish(self, session):
        """Shutdown all nodes."""
        nm = getattr(self, 'nodemanager', None)  # if not fully initialized
        if nm is not None:
            nm.teardown_nodes()

    def pytest_runtestloop(self):
        numnodes = len(self.nodemanager.specs)
        self.sched = LoadScheduling(numnodes, log=self.log)

        self.shouldstop = False
        while not self.session_finished:
            self.loop_once()
            if self.shouldstop:
                raise KeyboardInterrupt(str(self.shouldstop))
        return True

    @pytest.mark.trylast
    def pytest_runtest_logreport(self, report):
        if self.config.option.verbose >= 0 and report.when == "teardown":
            format_report_output(report.sections)


# -------------------------------------------------------------------------
# distributed testing initialization
# -------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption("--ip", action="append", dest="target_ips",
                     help="specify one or more ip addresses")
    parser.addoption("--U", "--user", action="append", dest="users",
                     help="specify one or more user credentials, in the form psnid!email:password")
    parser.addoption("-S", "-G", "--shared", "--global", action="store_true", dest="skynet_shared_config",
                     help="force usage of the shared config file (ignore the user config file)")
    parser.addoption("-C", "--config", dest="skynet_user_config",
                     help="specify a custom user config file extension, e.g.: skynet.<CONFIG>.conf. Default is 'user'")


def pytest_configure(config, __multicall__):
    __multicall__.execute()
    session = MantisSession(config)
    config.pluginmanager.register(session, "mantissession")

    if config.option.verbose >= 0:
        tr = config.pluginmanager.getplugin("terminalreporter")
        tr.showlongtestinfo = True

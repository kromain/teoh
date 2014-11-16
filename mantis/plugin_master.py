import pytest
import re
import sys

from mantis.configmanager import get_skynet_config, create_user_config_file
from xdist.dsession import DSession, LoadScheduling
from xdist.slavemanage import NodeManager
from skynet.config.config import Config


class InvalidIpError(Exception):
    pass


def validate_ip(ipstring):
    # ipv4 format [0-255].[0-255].[0-255].[0-255]
    p = re.compile('^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
    ip_matched = p.match(ipstring)
    valid = ip_matched is not None
    if valid:
        for part in ip_matched.groups():
            if not 0 <= int(part) <= 255:
                valid = False
                break

    if not valid:
        raise InvalidIpError("Target IP address '{}' is invalid!".format(ipstring))
    return ipstring


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

    def mantis_cmdline_ip_list(self):
        cmdline_iplist = []
        for iparg in self.config.getoption("target_ip", default=[], skip=True):
            cmdline_iplist.extend(iparg.split(","))
        return cmdline_iplist

    def mantis_cmdline_node_specs(self):
        return ["popen//id=Devkit <{}>//env:SKYNET_TARGET_IP={}".format(ip, validate_ip(ip))
                for ip in self.mantis_cmdline_ip_list()]

    def mantis_config_node_specs(self):
        return ["popen//id={} <{}>//env:SKYNET_TARGET_IP={}".format(tc.id, tc.ip, validate_ip(tc.ip))
                for tc in self._skynet_config.targets]

    @pytest.mark.trylast
    def pytest_sessionstart(self, session):
        """Creates and starts the nodes.

        The nodes are setup to put their events onto self.queue.  As
        soon as nodes start they will emit the slave_slaveready event.
        """

        self._skynet_config = get_skynet_config(self.config)

        # avoid infinite recursion by loading the plugin again in the spawned nodes
        self.config.option.plugins.remove("mantis.plugin_master")
        self.config.option.plugins.append("mantis.plugin_slave")

        # Command line args take precedence over config files
        node_specs = self.mantis_cmdline_node_specs()
        if not node_specs:
            node_specs = self.mantis_config_node_specs()
        elif self._skynet_config is None:
            print("*** NOTE: No Skynet user config file found in {}!".format(Config.project_dir()))
            print("      --> Creating 'skynet.user.conf' in folder using command arguments.")
            create_user_config_file(self.mantis_cmdline_ip_list())

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
    parser.addoption("--ip", action="append", dest="target_ip",
                     help="specify one or more ip addresses")
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

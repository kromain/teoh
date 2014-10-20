import pytest
import re
import skynet

from xdist.dsession import DSession, LoadScheduling
from xdist.slavemanage import NodeManager


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


def mantis_node_specs(pytest_config):
    # Command line args take precedence over config files
    cmdline_iplist = []
    for iparg in pytest_config.getoption("--ip", default=[], skip=True):
        cmdline_iplist.extend(iparg.split(","))
    if cmdline_iplist:
        return ["popen//id=Devkit <{}>//env:SKYNET_TARGET_IP={}".format(ip, validate_ip(ip))
                for ip in cmdline_iplist]

    return ["popen//id={} <{}>//env:SKYNET_TARGET_IP={}".format(tc.id, tc.ip, validate_ip(tc.ip))
            for tc in skynet.Config().targets]


class MantisSession(DSession):

    @pytest.mark.trylast
    def pytest_sessionstart(self, session):
        """Creates and starts the nodes.

        The nodes are setup to put their events onto self.queue.  As
        soon as nodes start they will emit the slave_slaveready event.
        """

        # avoid infinite recursion by loading the plugin again in the spawned nodes
        self.config.option.plugins.remove("mantis.plugin_master")
        self.config.option.plugins.append("mantis.plugin_slave")

        self.nodemanager = NodeManager(self.config, mantis_node_specs(self.config))
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


# -------------------------------------------------------------------------
# distributed testing initialization
# -------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption("--ip", action="append", help="specify one or more ip addresses")


def pytest_configure(config, __multicall__):
    __multicall__.execute()
    session = MantisSession(config)
    config.pluginmanager.register(session, "mantissession")
    tr = config.pluginmanager.getplugin("terminalreporter")
    # tr.showfspath = False

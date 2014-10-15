import py
import pytest
from xdist.dsession import DSession, LoadScheduling
from xdist.slavemanage import NodeManager



def mantis_node_specs():
    from skynet.config import Config
    config = Config()
    config.parse_json()

    return ["popen//id={} <{}>//env:SKYNET_TARGET_IP={}".format(tc.id, tc.ip, tc.ip) for tc in config.target_configs()]


class MantisSession(DSession):

    @pytest.mark.trylast
    def pytest_sessionstart(self, session):
        """Creates and starts the nodes.

        The nodes are setup to put their events onto self.queue.  As
        soon as nodes start they will emit the slave_slaveready event.
        """

        # avoid infinite recursion by loading the plugin again in the spawned nodes
        self.config.option.plugins.remove("mantisplugin")

        self.nodemanager = NodeManager(self.config, mantis_node_specs())
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

def pytest_configure(config, __multicall__):
    __multicall__.execute()
    session = MantisSession(config)
    config.pluginmanager.register(session, "mantissession")
    tr = config.pluginmanager.getplugin("terminalreporter")
    # tr.showfspath = False

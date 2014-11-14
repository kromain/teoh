from enum import Enum
from .deci4 import NetmpManager, Netmp, Tsmp

class Power(NetmpManager):
    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.netmp = super(Power,self).startnetmp(self.ip)

        self.tsmp = self.netmp.register(Tsmp)

    def stop(self):
        self.netmp.unregister(Tsmp)

        self.netmp = super(Power, self).stopnetmp(self.ip)
    
    def reboot(self):
        return self.tsmp.reboot()

    def power_off(self):
        return self.tsmp.power_off()

    def power_status(self):
        state = self.tsmp.get_power_status()
        return PowerState(state["powerState"])


class PowerState(Enum):
    DECI_READY = 1
    VSH_READY = 2
    SHUTDOWN_STARTED = 3
    GAMES_SHUTDOWN = 4
    ULP_MANAGER_EXITING = 5
    REBOOT_STARTED = 6
    GAMES_SHUTDOWN_REBOOT = 7
    ULP_MANAGER_EXITING_REBOOT = 8


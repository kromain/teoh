from enum import Enum
from .deci4 import NetmpManager, Netmp

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

        self.tsmp = self.netmp.register_tsmp()


    def stop(self):
        self.netmp.unregister_tsmp()

        self.netmp = super(Power, self).stopnetmp(self.ip)
    
    def reboot(self):
        return self.tsmp.reboot()

    def power_off(self):
        return self.tsmp.power_off()

    def power_status(self):
        state = self.tsmp.get_power_status()
        print(Status(state["powerState"])) 


class Status(Enum):
    DECI_Ready = 1
    VSH_Ready = 2
    Shutdown_Started = 3
    Games_Shutdown = 4
    ULP_Manager_Exiting = 5
    Reboot_Started = 6
    Games_Shutdown_reboot = 7
    ULP_Manager_Exiting_reboot = 8


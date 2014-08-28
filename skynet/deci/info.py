from .deci4 import NetmpManager, Netmp
from enum import Enum

class Info(NetmpManager):
    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.netmp = super(Info,self).startnetmp(self.ip)

        self.tsmp = self.netmp.register_tsmp()


    def stop(self):
        self.netmp.unregister_tsmp()

        self.netmp = super(Info, self).stopnetmp(self.ip)
    
    def is_user_signed_in(self, username):
        state = self.tsmp.get_psn_state(username)

        return state['result'] == 0 and state['psnState'] == 2

    def power_status(self):
        state = self.tsmp.get_power_status()
        print(status(state["powerState"]))



class status(Enum):
    DECI_Ready = 1
    VSH_Ready = 2
    Shutdown_Started = 3
    Games_Shutdown = 4
    ULP_Manager_Exiting = 5
    Reboot_Started = 6
    Games_Shutdown_reboot = 7
    ULP_Manager_Exiting_reboot = 8


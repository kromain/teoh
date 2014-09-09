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


        

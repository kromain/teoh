from .deci4 import NetmpManager, Netmp

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

        

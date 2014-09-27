from .deci4 import NetmpManager, Netmp, Tsmp
import os

try:
    from PIL import Image
    pil_loaded = True
except:
    pil_loaded = False

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

    def get_pict_blocks(self, mode=Tsmp.MODE_AUTO):
        for buffer in self.tsmp.get_pict(mode):
            yield buffer

    def get_pict(self, name, mode=Tsmp.MODE_AUTO):

        if '.' not in name:
            name = name + ".tga"

        in_name = name[:]

        if not name.endswith(".tga"):
            if not pil_loaded:
                raise Exception("PIL not installed so only .tga supported.  Do 'pip install Pillow' to enable image conversion.")

            in_name = name[:-4] + ".tga"

        fp = open(in_name, "wb")

        for buffer in self.tsmp.get_pict(mode):
            fp.write(buffer)

        if in_name != name:
            try:
                Image.open(in_name).save(name)
                os.remove(in_name)
            except KeyError:
                raise Exception(name[name.rfind('.'):] + " is not a valid file type")

        

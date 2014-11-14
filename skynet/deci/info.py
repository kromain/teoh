from .deci4 import NetmpManager, Netmp, Tsmp
import os
import threading

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
        self.tsmp = self.netmp.register(Tsmp)

    def stop(self):
        self.netmp.unregister(Tsmp)

        self.netmp = super(Info, self).stopnetmp(self.ip)
    
    def is_user_signed_in(self, username):
        state = self.tsmp.get_psn_state(username=username)

        return state['result'] == 0 and state['psnState'] == 2

    #TESTING: move to somewhere else
    def get_conf(self):
        return self.tsmp.get_conf()

    def get_info(self):
        res = self.tsmp.get_info()
        return {item["name"]:item["value"] for item in res["data"]}

    def get_pict_blocks(self, mode=Tsmp.MODE_AUTO):
        for buffer in self.tsmp.get_pict(mode):
            yield buffer

    def _get_pict_thread(self, name, mode):
        if '.' not in name:
            name = name + ".tga"

        in_name = name[:]

        if not name.endswith(".tga"):
            if not pil_loaded:
                raise Exception("PIL not installed so only .tga supported.  Do 'pip install Pillow' to enable image conversion.")

            in_name = name[:-4] + ".tga"

        fp = open(in_name, "wb")

        cnt = 0
        for buffer in self.tsmp.get_pict(mode):
            cnt += 1
            fp.write(buffer)
        fp.close()


        if in_name != name:
            try:
                Image.open(in_name).save(name)
                os.remove(in_name)
            except KeyError:
                raise Exception(name[name.rfind('.'):] + " is not a valid file type")

    def get_pict(self, name, mode=Tsmp.MODE_AUTO, async = False):

        if not async:
            self._get_pict_thread(name, mode)

        else:
            thread = threading.Thread(name="GetPictThread",
                                      target=self._get_pict_thread,
                                      args=(name, mode))
            thread.start()

            return thread

        

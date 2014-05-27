import sys
import time
from deci4 import Netmp, NetmpManager

class Console(NetmpManager):
    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.netmp = super(Console,self).startnetmp(self.ip)

        self.ttyp = self.netmp.register_ttyp()


    def stop(self):
        self.netmp.unregister_ttyp()

        self.netmp = super(Console, self).stopnetmp(self.ip)

    def read(self):
        res = self.ttyp.read()
        if res:
            if "message" in res:
                if len(res["message"]) > 1:
                    return ("{port}:{category}:{tid:x}:{pid:x}:{message}".format(**res))

        return None


if __name__ == "__main__":


    with Console(ip=sys.argv[1]) as console:

        try:
            while True:
                line = console.read()
                if line:
                    print (line)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("Closing connection")


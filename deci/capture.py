import sys
import datetime
import threading
import time
import struct
from deci4 import Netmp

class CaptureThread(threading.Thread):

    def run(self):
        self.stop = False
        self.blocks = []

        netmp = Netmp(ip=sys.argv[1])

        netmp.connect()

        ctrlp = netmp.register_ctrlp()

        ctrlp.rec_start()

        start = datetime.datetime.now();
        while not self.stop:
            self.blocks.append(ctrlp.read_raw_data())

        ctrlp.rec_stop()

        netmp.unregister_ctrlp()

        netmp.disconnect()


thread = CaptureThread()

thread.start()

sys.stdin.read(1)

thread.stop = True

thread.join()

print "%d blocks read" % len(thread.blocks)

f = open("capture.dat", "wb")
for block in thread.blocks:
    f.write(struct.pack("@I", len(block)))
    f.write(block)


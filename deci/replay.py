import sys
import datetime
import time
import struct
import array
from deci4 import Netmp


blocks = []

with open("capture.dat", "rb") as f:
    while True:
        length = f.read(4)

        if not length: 
            break

        length = struct.unpack("@I", length)[0]

        str = f.read(length)
        arr = array.array('B')
        arr.fromstring(str)
        blocks.append(arr)

print "%d blocks read" % len(blocks)


netmp = Netmp(ip=sys.argv[1])

netmp.connect()

ctrlp = netmp.register_ctrlp()

ctrlp.play_start()

for block in blocks:
    ctrlp.play_raw_data(block)
    time.sleep(0.01)

ctrlp.play_stop()

netmp.unregister_ctrlp()

netmp.disconnect()

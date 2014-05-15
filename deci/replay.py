import sys
import datetime
import time
import struct
import array
from deci4 import Netmp


with open("capture.dat", "rb") as f:
    netmp = Netmp(ip=sys.argv[1])

    netmp.connect()

    ctrlp = netmp.register_ctrlp()

    ctrlp.play_start()

    while True:
        length = f.read(4)

        if not length: 
            break

        length = struct.unpack("@I", length)[0]

        str = f.read(length)
        arr = array.array('B')
        arr.fromstring(str)

        ctrlp.play_raw_data(arr)



    ctrlp.play_stop()

    netmp.unregister_ctrlp()

    netmp.disconnect()

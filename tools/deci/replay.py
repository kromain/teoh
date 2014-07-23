import array
import struct
import sys

from skynet.deci.deci4 import Netmp


if len(sys.argv) < 2:
    print("USAGE replay.py IPADDRESS")
    quit()

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

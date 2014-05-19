import sys
import datetime
from deci4 import Netmp

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

ctrlp = netmp.register_ctrlp()

ctrlp.rec_start()

start = datetime.datetime.now();
while( datetime.datetime.now() - start).seconds < 5:
    data = ctrlp.read_data()
    print(len(data["data"]))
    for line in data["data"]:
        print("Timestamp ", line["timestamp"], " buttons", hex(line["buttons"]))

ctrlp.rec_stop()

netmp.unregister_ctrlp()

netmp.disconnect()




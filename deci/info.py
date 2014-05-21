import sys
from deci4 import Netmp,make_dump

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

tsmp = netmp.register_tsmp()

#print (tsmp.get_conf())

info = tsmp.get_info()
print (info)

#for item in info["data"]:
#    if "value" in item:
#        print (item["name"], item["value"])
#    else:
#        print (item["name"], "????")

netmp.unregister_tsmp()

netmp.disconnect()

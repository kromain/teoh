import sys

from .deci4 import Netmp

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

for l in netmp.get_registered_list()["data"]:
    print ("%x: %s" % (l["protocol"], l["owner"]))

owner = netmp.get_owner()
if owner:
    print ("Owned by %s" % owner)

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

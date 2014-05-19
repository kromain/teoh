import sys
from deci4 import Netmp

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

ttyp = netmp.register_ttyp()

#print ("Conf", ttyp.get_conf())

while True:
    print (ttyp.read()["message"])


netmp.unregister_ttyp()

netmp.disconnect()



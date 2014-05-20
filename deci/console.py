import sys
from deci4 import Netmp

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

ttyp = netmp.register_ttyp()

try:
    while True:
        res = ttyp.read()
        if res:
            if "message" in res:
                if len(res["message"]) > 1:
                    print ("%s" % res["message"])

except KeyboardInterrupt:
    print("Closing connection")

netmp.unregister_ttyp()

netmp.disconnect()



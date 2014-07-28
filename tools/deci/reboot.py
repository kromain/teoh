import sys

from skynet.deci.deci4 import Netmp

netmp = Netmp(ip=sys.argv[1])

netmp.connect()

tsmp = netmp.register_tsmp()

tsmp.reboot()

netmp.unregister_tsmp()

netmp.disconnect()

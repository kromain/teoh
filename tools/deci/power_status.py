import sys
import struct

from skynet.deci.deci4 import Netmp

while(True):

	try:
		netmp = Netmp(ip=sys.argv[1])
		netmp.connect()
		tsmp = netmp.register_tsmp()
		print("\n***************************************************************\n")
		res = tsmp.get_power_status()
		print("powerState:")
		print(res["powerState"])
		print("\n***************************************************************\n")
		netmp.unregister_tsmp()
		netmp.disconnect()

	except ConnectionRefusedError:
		print("1")
		pass

	except ConnectionResetError:
		print("2")
		pass

	except struct.error:
		print("3")
		pass
import sys
import struct

from skynet.deci.deci4 import Netmp
from skynet.deci.power import Power

if __name__ == "__main__":
	try:
		with Power(ip=sys.argv[1]) as power:
			print(power.power_status())

	except IndexError:
		print("USAGE power_status.py IPADDRESS")

	except ConnectionRefusedError:
		pass

	except ConnectionResetError:
		pass

	except struct.error:
		pass


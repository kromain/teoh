import sys
from skynet.deci.power import Power


if __name__ == "__main__":

    try:
        with Power(ip=sys.argv[1]) as power:
            power.power_off()

    except IndexError:
        print("USAGE info.py IPADDRESS")


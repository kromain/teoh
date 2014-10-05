import sys

#from skynet.deci.deci4 import Netmp

#netmp = Netmp(ip=sys.argv[1])

#netmp.connect()

#for l in netmp.get_registered_list()["data"]:
    #print ("%x: %s" % (l["protocol"], l["owner"]))

#owner = netmp.get_owner()
#if owner:
    #print ("Owned by %s" % owner)

#tsmp = netmp.register_tsmp()

#print (tsmp.get_conf())

#info = tsmp.get_info()
#print (info)

#print ("steve-e1", tsmp.get_psn_state("steve-e1"))
#print ("steve-e2", tsmp.get_psn_state("steve-e2"))
#print ("steve082214hkb", tsmp.get_psn_state("steve082214hkb"))

#netmp.unregister_tsmp()
#
#netmp.disconnect()

from skynet.deci.info import Info
from skynet.deci.power import Power


if __name__ == "__main__":

    try:
        with Info(ip=sys.argv[1]) as info, Power(ip=sys.argv[1]) as power:

            print("CONF:", info.get_conf())
            if info.is_user_signed_in("steve-e1"):
                print("Yes")
            else:
                print("No")

            print(power.power_status())

            infolist = info.get_info()
            for item in infolist:
                print (item,infolist[item])

    except IndexError:
        print("USAGE info.py IPADDRESS")


import sys

from skynet.deci.info import Info

def dotted(val):
    return "%s.%s.%s.%s" % ( val & 0xFF, (val >> 8) & 0xFF, (val >> 16) & 0xFF, (val >> 24) & 0xff)

if __name__ == "__main__":

    try:
        with Info(ip=sys.argv[1]) as info:

            if info.is_user_signed_in("steve-e1"):
                print("Yes")
            else:
                print("No")

            infolist = info.get_info()
            for item in infolist:
                if type(infolist[item]) == int:
                    if item in["GameLanIpAddress",
                                "GameLanSubnetMask",
                                "SdkVersion",
                                "SubnetMask"]:
                        print (item,dotted(infolist[item]))
                    else:
                        print (item,infolist[item])
                elif type(infolist[item]) == bytes:
                    print(item, ''.join([hex(b)[2:] for b in infolist[item]]))
                elif type(infolist[item]) == str:
                    print (item,infolist[item])


    except IndexError:
        print("USAGE info.py IPADDRESS")


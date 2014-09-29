import sys
from skynet.deci.info import Info


if __name__ == "__main__":

    try:
        with Info(ip=sys.argv[1]) as info:

            if info.is_user_signed_in("steve-e1"):
                print("Yes")
            else:
                print("No")

            print("Read game")
            info.get_pict("GAME" + sys.argv[2])
            print("Read system")
            info.get_pict("SYSTEM" + sys.argv[2])
            print("Read auto")
            info.get_pict("AUTO" + sys.argv[2])


    except IndexError:
        print("USAGE screenshot.py IPADDRESS FILE")



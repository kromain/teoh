import sys
import time
from skynet.deci.info import Info


#def screenshotthread(info, filename):
#    info.get_pict(filename)
        
    

if __name__ == "__main__":

    try:
        with Info(ip=sys.argv[1]) as info:
            info.get_pict(sys.argv[2])
  
    except IndexError:
        print("USAGE screenshot.py IPADDRESS FILE")


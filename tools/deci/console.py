import sys
import time

from skynet.deci.console import Console


if __name__ == "__main__":

    try:
        with Console(ip=sys.argv[1]) as console:

            try:
                while True:
                    line = console.readsync()
                    if line:
                        print (line)
                    else:
                        time.sleep(0.01)
            except KeyboardInterrupt:
                print("Closing connection")
    except IndexError:
        print("USAGE console.py IPADDRESS")


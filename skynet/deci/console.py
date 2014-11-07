import sys
import time

from .deci4 import NetmpManager,Ttyp

class Console(NetmpManager):
    """
    The interface to the TTY console on the target.

    This class allows retrieving the global output from the TTY console on the target. This is the same output that
    the Neighborhood Console Output retrieves.

    The output is retrieved line by line as long as there's data available. If there's no data available,
    :meth:`read()` will return immediately without blocking while :meth:`readsync()` will block until a line is
    available.
    """
    def __init__(self, ip):
        self.ip = ip

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.netmp = super(Console,self).startnetmp(self.ip)

        self.ttyp = self.netmp.register(Ttyp)


    def stop(self):
        self.netmp.unregister(Ttyp)

        self.netmp = super(Console, self).stopnetmp(self.ip)

    def get_port_states(self):
        return self.ttyp.get_port_states()

    def read(self):
        """ Returns the next buffered line of output from the TTY console, or return immediately if there's no data.

        :return: One line of output as String, or None if no TTY data is immediately available.
        """
        res = self.ttyp.read()
        if res:
            # It would be better to check the message type somehow
            if "message" in res:
                # Console likes to send "\n" between every line
                if len(res["message"]) > 1:
                    return ("{port}:{category}:{tid:x}:{pid:x}:{message}".format(**res))

        return None

    def readsync(self):
        """ Returns the next buffered line of output from the TTY console, or wait until more data becomes available.

        :return: One line of output as String, whenever the next one is available.
        """
        while True:
            res = self.ttyp.readsync()

            if len(res["message"]) > 1:
                return ("{port}:{category}:{tid:x}:{pid:x}:{message}".format(**res))


if __name__ == "__main__":


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


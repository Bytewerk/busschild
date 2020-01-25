import sys

class posdisplay():
    """
    Represent an ESP8266-equipped BA66 display connected by TCP/IP.
    """
    def __init__(self, sock):
        """ Create a new display.
            sock: The socket via which the display is connecting.
        """
        self.sock = sock

    def clear(self):
        """ Clear display contents. """
        self.write(b'\x1B[2J')

    def position_cursor(self, x, y):
        """ Position the cursor. """
        self.write("\x1B[{0:d};{1:d}H".format(y&0xFF, x&0xFF))

    def reset(self):
        """ Set cursor to x=0, y=0, and clear the display. """
        self.clear()
        self.position_cursor(0, 0)

    def write(self, data):
        if self.sock:
            if isinstance(data, str):
                self.sock.send(bytes(data,'cp850'))
            else:
                self.sock.send(data)
        else:
            sys.stderr.write(repr(data).replace('\x1b','\\x1B'))

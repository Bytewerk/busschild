import serial
import sys

class posdisplay():
    """
    Represent the BA66 display.
    """
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, **kwargs):
        self.ser = None
        try:
            self.ser = serial.Serial(port, baudrate, **kwargs)
        except serial.SerialException:
            print("Can't open port, using sys.stderr for debugging.", file=sys.stderr)

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
        if self.ser:
            if isinstance(data, str):
                self.ser.write(bytes(data,'latin-1'))
            else:
                self.ser.write(data)
        else:
            sys.stderr.write(repr(data).replace('\x1b','\\x1B'))

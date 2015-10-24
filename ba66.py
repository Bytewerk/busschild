import serial

class posdisplay():
    """
    Represent the BA66 display.
    """
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate, timeout=2, rtscts=1)

    def clear(self):
        """ Clear display contents. """
        self.ser.write(b'\x1B[2J')

    def position_cursor(self, x, y):
        """ Position the cursor. """
        self.write("\x1B[{0:d};{1:d}H".format(y&0xFF, x&0xFF))

    def write(self, data):
        if isinstance(data, str):
            self.ser.write(bytes(data, 'cp850'))
        else:
            self.ser.write(data)

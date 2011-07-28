"""
Driver for the Stanford Research PRS10 Rubidium Clock
"""
import serial
import os

class Clock:
    """
    Rubidium clock that can be used with an 1 pulse-per-second (1PPS) signal to
    keep it accurate. Controlled through serial (RS-232) interface
    """
    __ser = None # The private interface to the device

    def __init__(self, COM=0):
        """ Connecting to the device """
        # Get serial port name on Linux or other (i.e. Windows) system
        if os.name == "posix":
            portbase = '/dev/ttyUSB'
        else:
            portbase = 'COM'
        comport = '%s%d' %(portbase, COM)
        # Settings from the manual
        try:
            self.__ser = serial.Serial(comport,
                                       baudrate=9600,
                                       bytesize=8,
                                       stopbits=2,
                                       parity=serial.PARITY_NONE,
                                       xonxoff=1,
                                       timeout=1,
                                       )
        except (serial.serialutil.SerialException):
            raise IOError("Couldn't open port %s" %(comport))

    def write(self, message):
        """ Write to the device """
        self.__ser.write("%s\r" %message) # Adding the line-feed that is the command delimiter

    def read(self):
        """ Read one line from the device """
        return self.__ser.readline()

    def ask(self, query):
        """ Write a command and listen for answer """
        self.write(query)
        return self.read()

    def setupWithGPS(self):
        """ Reset settings suitable for 1PPS stabilization from GPS """
        clock.write("LM1") # Enable digital pre-filter for the incoming 1PPS signal from GPS
        clock.write("PT14") # Set longest PLL parameter for 1PPS input with bad short-term stability

if __name__ == "__main__":
    from sys import exit
    com = int(raw_input("Serial port number (the X in COMX or ttyUSBX): "))
    try:
        clock = Clock(com)
    except IOError:
        print "Port no good..."
        exit(1)

    # If all good:
    print "Unit ID: %s" %(clock.ask("ID?"))

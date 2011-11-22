import serial
import os

class PowerMeter:
    """ GWInstek GDM-396 power meter """

    port = None

    def __init__(self, port=None):
        """ Inital connection automatically """
        if os.name == 'posix':
            portbase = '/dev/ttyUSB'
        else:
            portbase = 'COM'


        if port is None:
            ports = xrange(10)
        else:
            ports = [port]

        for i in ports:
            try:
                self.ser = serial.Serial("%s%d" %(portbase, i),
                                         baudrate=2400,
                                         bytesize=8,
                                         stopbits=1,
                                         parity=serial.PARITY_NONE,
                                         timeout=1)
                self.port = i
                # Required, from snooping
                self.ser.setRTS(0)
                self.ser.setRTS(0)
                self.ser.setDTR(1)
                self.ser.setDTR(1)
                break
            except serial.SerialException:
                self.ser = None

        if self.ser is None:
            print "No connection...."
            return None
        else:
            print "Powermeter connected on %s%d" %(portbase, self.port)


    def read(self):
        reply = self.ser.read(14) # every data should be 14 bits
        print len(reply)
        return reply

if __name__ == "__main__":

    pm = PowerMeter()
    print pm.read()

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
                                         timeout=5,
                                         xonxoff=1)
                self.port = i
                # Required, from snooping
                self.ser.setRTS(0)
                self.ser.setRTS(0)
                self.ser.setDTR(1)
                self.ser.setDTR(1)
                self.read(1) # needs to read and throw away this one byte
                break
            except serial.SerialException:
                self.ser = None

        if self.ser is None:
            print "No connection...."
            return None
        else:
            print "Powermeter connected on %s%d" %(portbase, self.port)


    def read(self, bytes=14):
        reply = self.ser.read(bytes) # every data should be 14 bits
        # # Sometimes it's losing some bytes, this synchronization does not work
        # if len(reply) < bytes:
        #     print "underrun... continue"
        #     reply += self.read(bytes - len(reply))
        return reply

    def getnumber(self, data=None):
        if data is None:
            data = self.read()

        toprint = ""
        for c in data:
            toprint += "%x " %ord(c)
        return toprint

if __name__ == "__main__":

    pm = PowerMeter(3)
    # print pm.read()
    from time import sleep
    while True:
        print pm.getnumber()
        sleep(0.1)

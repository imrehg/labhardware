import serial
import os

class MultiMeter:
    """ GWInstek GDM-396 multi meter """

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
        return reply

    def getnumber(self, data=None):
        if data is None:
            data = self.read()
        return self.translate(data)

    def translate(self, msg):
        cnum = {63: 0, 6: 1, 91: 2, 79: 3, 102: 4, 109: 5, 125: 6, 7: 7, 127: 8, 111: 9}
        if len(msg) != 14:
            return None
        s = {}  # settings
        d = [0, 0, 0, 0]  # digits
        multiplier = 1
        untit = ""

        for c in msg:
            n = ord(c)
            upper = n / 16
            if (upper == 0x1):
                if (n & 0x1):
                    s['rs232'] = True
                if (n & 0x2):
                    s['auto'] = True
                if (n & 0x4):
                    s['dc'] = True
                if (n & 0x8):
                    s['ac'] = True

            elif (upper == 0x2):
                if (n & 0x1):
                    d[0] |= 0b1
                if (n & 0x2):
                    d[0] |= 0b100000
                if (n & 0x4):
                    d[0] |= 0b10000
                if (n & 0x8):
                    multiplier *= -1
            elif (upper == 0x3):
                if (n & 0x1):
                    d[0] |= 0b10
                if (n & 0x2):
                    d[0] |= 0b1000000
                if (n & 0x4):
                    d[0] |= 0b100
                if (n & 0x8):
                    d[0] |= 0b1000

            elif (upper == 0x4):
                if (n & 0x1):
                    d[1] |= 0b1
                if (n & 0x2):
                    d[1] |= 0b100000
                if (n & 0x4):
                    d[1] |= 0b10000
                if (n & 0x8):
                    multiplier *= 0.001
            elif (upper == 0x5):
                if (n & 0x1):
                    d[1] |= 0b10
                if (n & 0x2):
                    d[1] |= 0b1000000
                if (n & 0x4):
                    d[1] |= 0b100
                if (n & 0x8):
                    d[1] |= 0b1000

            elif (upper == 0x6):
                if (n & 0x1):
                    d[2] |= 0b1
                if (n & 0x2):
                    d[2] |= 0b100000
                if (n & 0x4):
                    d[2] |= 0b10000
                if (n & 0x8):
                    multiplier *= 0.01
            elif (upper == 0x7):
                if (n & 0x1):
                    d[2] |= 0b10
                if (n & 0x2):
                    d[2] |= 0b1000000
                if (n & 0x4):
                    d[2] |= 0b100
                if (n & 0x8):
                    d[2] |= 0b1000

            elif (upper == 0x8):
                if (n & 0x1):
                    d[3] |= 0b1
                if (n & 0x2):
                    d[3] |= 0b100000
                if (n & 0x4):
                    d[3] |= 0b10000
                if (n & 0x8):
                    multiplier *= 0.1
            elif (upper == 0x9):
                if (n & 0x1):
                    d[3] |= 0b10
                if (n & 0x2):
                    d[3] |= 0b1000000
                if (n & 0x4):
                    d[3] |= 0b100
                if (n & 0x8):
                    d[3] |= 0b1000

            elif (upper == 0xa):
                if (n & 0x1):
                    s['diode'] = True
                if (n & 0x2):
                    multiplier *= 1e3
                if (n & 0x4):
                    multiplier *= 1e-9
                if (n & 0x8):
                    multiplier *= 1-6
            elif (upper == 0xb):
                if (n & 0x1):
                    s['beep'] = True
                if (n & 0x2):
                    multiplier *= 1e6
                if (n & 0x4):
                    unit = "%"
                if (n & 0x8):
                    multiplier *= 1e-3
            elif (upper == 0xc):
                if (n & 0x1):
                    s['Hold'] = True
                if (n & 0x2):
                    s['Delta'] = True
                if (n & 0x4):
                    unit = "R"
                if (n & 0x8):
                    unit = "F"
            elif (upper == 0xd):
                if (n & 0x1):
                    s['battery'] = True
                if (n & 0x2):
                    unit = "Hz"
                if (n & 0x4):
                    unit = "V"
                if (n & 0x8):
                    unit = "A"
            elif (upper == 0xe):
                if (n & 0x1):
                    unit = "C"

        try:
            value = multiplier * (cnum[d[0]] * 1000 +
                                  cnum[d[1]] * 100 +
                                  cnum[d[2]] * 10 +
                                  cnum[d[3]]
                                  )
        except (KeyError):
            return None

        s['unit'] = unit
        s['value'] = value
        return s

if __name__ == "__main__":

    mm = MultiMeter(4)
    # print pm.read()
    from time import sleep
    while True:
        print mm.getnumber()
        sleep(0.1)

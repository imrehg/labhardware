import  serial
from re import match
from time import time

class AgilentMultimeter:

    def __init__(self, com, baud):
        self.__ser = serial.Serial(port="%s"%(com),baudrate=baud, bytesize=7, \
            stopbits=2, parity=serial.PARITY_EVEN, timeout=2)
        print "Connected to: %s " %(self.__ser.portstr)
        if (not self.__TestConnection()):
            print "No Multimeter on this port...."
            self.close()
            return None
        else:
            print "Multimeter found"

    def close(self):
        print "Closing COM port"
        self.__ser.close()

    def __TestConnection(self):
        ''' Test if there's really a multimeter connected '''
        id = self.getID()
        if (match(".*,34401A,.*", id)):
            found = True
        else:
            found = False
        return found

    def __SendCmd(self, cmd):
        ''' Send command on serial line '''
        cmdout = "%s\r\n" %(cmd)
        self.__ser.write(cmdout)

    def __GetReply(self):
        ''' Read answer on serial line '''
        return self.__ser.readline()

    def Query(self, cmd):
        ''' Send Query and wait for answer '''
        self.__SendCmd(cmd)
        return self.__GetReply()

    def getID(self):
        ''' Get device ID '''
        cmd = "*IDN?"
        return self.Query(cmd)

    def Set(self, cmd):
        ''' Send a command without waiting for an answer '''
        try:
            self.__SendCmd(cmd)
        except:
            return 1
        return 0


combase = "/dev/ttyUSB"
i = 0
baud = 9600
multimeter = AgilentMultimeter("%s%d" %(combase, i), baud)

multimeter.Set("*CLS")
multimeter.Set("ZERO:AUTO ONCE")
multimeter.Set("CONF:VOLT:DC 1,0.00001")
multimeter.Set("SYSTem:REMote")
for i in range(0,10):
    start = time()
    print "Read: %f" %(float(multimeter.Query("READ?")))
    total = time() - start
    print "-> Time: %f" %(total)

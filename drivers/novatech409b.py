import serial
import os

class N409B:
    """ Novatech 409B 171 MHz 4-channel signal generator """

    port = None

    def __init__(self):
        """ Inital connection automatically """
        if os.name == 'posix':
            portbase = '/dev/ttyUSB'
        else:
            portbase = 'COM'

        for i in xrange(10):
            try:
                self.ser = serial.Serial("%s%d" %(portbase, i),
                                         baudrate=19200,
                                         bytesize=8,
                                         stopbits=1,
                                         parity=serial.PARITY_NONE,
                                         timeout=1)
                self.setEcho(off=True)
                self.port = i
                break
            except:
                self.ser = None

        if self.ser is None:
            print "No connection...."
            return None
        else:
            print "Synthetizer connected on %s%d" %(portbase, self.port)

    def sendCmd(self, command):
        self.ser.write("%s\n" %(command))

    def readReply(self):
        return(self.ser.readline().strip())

    def query(self, command):
        self.sendCmd(command)
        return self.readReply()

    def setEcho(self, off=True):
        cmd = 'D' if off else 'E'
        answer = self.query(cmd)
        return answer == 'OK'

    def getSettings(self):
        self.sendCmd("QUE")
        for i in xrange(5):
            print self.readReply()

    def setFreq(self, channel, value):
        if (value > 171.1276031) || (value < 0):
            return False

        cmd = ""

if __name__ == "__main__":
    synth = N409B()

    print synth.getSettings()

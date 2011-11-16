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
                good = self.setEcho(off=True)
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
        cmd = 'E D' if off else 'E E'
        answer = self.query(cmd)
        return answer == 'OK'

    def getSettings(self):
        self.sendCmd("QUE")
        for i in xrange(5):
            print self.readReply()

    def setFreq(self, channel, value):
        channel = int(channel)
        value = float(value)
        assert(channel in [0, 1, 2, 3])
        if (value > 171.1276031) | (value < 0.0):
            return False

        cmd = "F%d %3.7f" %(channel, value)
        reply = self.query(cmd)
        result = "Bad frequency" if reply == "?1" else reply
        return result

    def channelOff(self, channel):
        """ Turn channel off by setting frequency to 0 """
        assert(channel in [0, 1, 2, 3])
        answer = self.setFreq(channel, 0)
        return answer

    def setPhase(self, channel, phase):
        pass

    def setLevel(self, channel, level):
        """ Set voltage level """
        channel = int(channel)
        level = int(level)
        assert(channel in [0, 1, 2, 3])
        if level < 0:
            level = 0
        elif level > 1024:
            level = 1024
        cmd = "V%d %d" %(channel, level)
        reply = self.query(cmd)
        result = "Bad amplitude" if reply == "?7" else reply
        return result

if __name__ == "__main__":
    synth = N409B()

    print synth.getSettings()
    print synth.setFreq(0, 0.1*5)

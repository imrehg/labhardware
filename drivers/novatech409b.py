import serial
import os

class N409B:
    """ Novatech 409B 171 MHz 4-channel signal generator """

    port = None
    channels = []

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
                self.setupChannels()
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
        reply = []
        for i in xrange(5):
            reply += [self.readReply()]
        return reply

    def setupChannels(self):
        """ Save current settings from synth """
        settings = self.getSettings()
        for i in xrange(4):
            freq = int(settings[i][0:8], 16)/10000000.0 # each step is in 0.1Hz
            amp = int(settings[i][14:18], 16)
            phase = int(settings[i][9:13], 16)
            self.channels += [{'no': i, 'freq': freq, 'amp': amp, 'phase': phase}]
        print self.channels

    def setFreq(self, channel, value):
        channel = int(channel)
        value = float(value)
        assert(channel in [0, 1, 2, 3])
        if (value > 171.1276031) | (value < 0.0):
            return False

        cmd = "F%d %3.7f" %(channel, value)
        reply = self.query(cmd)
        if reply == "OK":
            channels[channel]['freq'] = value
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
        if reply == "OK":
            channels[channel]['amp'] = level
        result = "Bad amplitude" if reply == "?7" else reply
        return result

    def setPhase(self, channel, phase):
        """ Set phase """
        channel = int(channel)
        phase = int(phase)
        assert(channel in [0, 1, 2, 3])
        if level < 0:
            level = 0
        elif level > 16383:
            level = 16383
        cmd = "P%d %d" %(channel, phase)
        reply = self.query(cmd)
        if reply == "OK":
            channels[channel]['phase'] = phase
        result = "Bad phase" if reply == "?4" else reply
        return result

if __name__ == "__main__":
    synth = N409B()

    print synth.getSettings()
    print synth.setFreq(0, 0.1*5)

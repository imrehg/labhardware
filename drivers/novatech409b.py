import serial
import os
import numpy as np

class N409B:
    """ Novatech 409B 171 MHz 4-channel signal generator """

    port = None
    channels = {}

    def __init__(self):
        """ Inital connection automatically """
        if os.name == 'posix':
            portbase = '/dev/ttyUSB'
        else:
            portbase = 'COM'

        self.ser = None
        for i in xrange(20):
            try:
                self.ser = serial.Serial("%s%d" %(portbase, i),
                                         baudrate=19200,
                                         bytesize=8,
                                         stopbits=1,
                                         parity=serial.PARITY_NONE,
                                         timeout=1)
                if self.setEcho(off=True):
                    self.port = i
                    self.setupChannels()
                    break
                else:
                    self.ser = None
            except (serial.SerialException):
                pass

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
        good = True if settings else False
        try:
            for i in xrange(4):
                freq = int(settings[i][0:8], 16)/10000000.0 # each step is in 0.1Hz
                amp = int(settings[i][14:18], 16)
                phase = int(settings[i][9:13], 16)
                self.channels[i] = {'freq': freq, 'amp': amp, 'phase': phase}
        except (ValueError):
            good = False
        return good


    def setFreq(self, channel, value):
        channel = int(channel)
        value = float(value)
        assert(channel in [0, 1, 2, 3])
        if (value > 171.1276031) | (value < 0.0):
            return False

        cmd = "F%d %3.7f" %(channel, value)
        reply = self.query(cmd)
        if reply == "OK":
            self.channels[channel]['freq'] = value
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
            self.channels[channel]['amp'] = level
        result = "Bad amplitude" if reply == "?7" else reply
        return result

    def setPhase(self, channel, phase):
        """ Set phase """
        channel = int(channel)
        phase = int(phase)
        assert(channel in [0, 1, 2, 3])
        if phase < 0:
            phase = 0
        elif phase > 16383:
            phase = 16383
        cmd = "P%d %d" %(channel, phase)
        reply = self.query(cmd)
        if reply == "OK":
            self.channels[channel]['phase'] = phase
        result = "Bad phase" if reply == "?4" else reply
        return result

    def getChannels(self):
        return self.channels

    def __freqToHex(self, freq):
        """ Turn frequency in MHz into binary value for output """
        return '{:08x}'.format(int(freq * 1e7))

    def setupTable(self, table):
        cmds = ["m 0"]
        ch = 0
        i = 0
        for t in table:
            cmds += ["t%d %s %s,%s,%s,%s" %(ch, '{:04x}'.format(i), self.__freqToHex(t[0]), '0000', '{:04x}'.format(t[2]), '{:02x}'.format(t[3]))]
            ch = 1 - ch
            if ch == 0:
                i += 1
        cmds += ["m t"]
        for c in cmds:
            # print c
            self.sendCmd(c)
        pass

    def sweep(self, params):
        """ Run a sweep with the given parameters """
        startfreq0 = params['sfreq0']
        finishfreq0 = params['ffreq0']
        startfreq1 = params['sfreq1']
        finishfreq1 = params['ffreq1']
        totaltime = params['totaltime']
        stepsize = params['stepsize']
        repeat = params['repeat']
        nsteps = int(totaltime / stepsize * 1e4) + 1

        freq0 = np.linspace(startfreq0, finishfreq0, nsteps)  # in MHz units
        freq1 = np.linspace(startfreq1, finishfreq1, nsteps)  # in MHz units

        stepstring = '{:02x}'.format(stepsize)
        cmds = ["m 0"]
        for i in range(nsteps):
            thisstep = stepstring if ((i < (nsteps-1)) or repeat) else 'ff'
            cmds += ["t0 %s %s,%s,%s,%s" %('{:04x}'.format(i), self.__freqToHex(freq0[i]), '0000', '03ff', thisstep)]
            cmds += ["t1 %s %s,%s,%s,%s" %('{:04x}'.format(i), self.__freqToHex(freq1[i]), '0000', '03ff', thisstep)]
        cmds += ["t0 %s %s,%s,%s,%s" %('{:04x}'.format(nsteps), self.__freqToHex(freq0[0]), '0000', '03ff', '00')]
        cmds += ["t1 %s %s,%s,%s,%s" %('{:04x}'.format(nsteps), self.__freqToHex(freq1[0]), '0000', '03ff', '00')]
        cmds += ["m t"]
        import time
        for c in cmds:
            self.sendCmd(c)
        return True

    def trigger(self):
        """ Send software trigger """
        self.sendCmd("ts");

if __name__ == "__main__":
    synth = N409B()

    print synth.getSettings()

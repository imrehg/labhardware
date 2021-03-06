import visa
from re import match

class Counter:

    def __init__(self, gpib):
        ''' Initialize device '''
        self.device = visa.instrument("GPIB::%d" %(gpib))
        if (not self.__TestConnection()):
            print "No counter on this gpib channel..."
            return None
        else:
            print "Counter found"

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        if (match(".*,53230A,.*", id)):
            found = True
        else:
            found = False
        return found

    def reset(self):
        ''' Reset and clear device '''
        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write("*SRE 0")
        self.device.write("*ESE 0")
        self.device.write(":STAT:PRESET")

    # def setupFast(self):
    #     ''' Set up parameters for fast measurement
    #     This follows the Programming Guide example,
    #     except trying to keep the precision higher
    #     '''
    #     self.device.write(":FORMAT:ASCII")
    #     self.device.write(":EVENT1:LEVEL 0")
    #     self.device.write(":DISP:ENAB OFF")
    #     # Turn off mathematics
    #     self.device.write(":CALC:MATH:STATE OFF")
    #     self.device.write(":CALC2:LIM:STATE OFF")
    #     self.device.write(":CALC3:AVER:STATE OFF")
    #     # Turn off printing
    #     self.device.write(":HCOPY:CONT OFF")
    #     # Redefine trigger
    #     # self.device.write("*DDT #15FETC?")

    # def setupGating(self, gatetime):
    #     self.device.write(":FREQ:ARM:STAR:SOUR IMM")
    #     self.device.write(":FREQ:ARM:STOP:SOUR TIM")
    #     self.device.write(":FREQ:ARM:STOP:TIM %f" %(gatetime))

    def setupFreq(self, channel=1, gatetime=1):
        commands = ["CONF:FREQ (@%s)" %(channel),
                    "TRIG:SOUR IMM",
                    "SAMPLE:COUNT MAX",
                    "SENS:FREQ:MODE CONT",
                    "SENS:FREQ:GATE:TIME %g" %(gatetime),
                    "SENS:FREQ:GATE:SOUR TIME",
                    "CALC:STAT OFF",
                    ]
        for cmd in commands:
            self.device.write(cmd)

    def setupFreqBatch(self, channel=1, count=1, gatetime=1):
        """ Software triggered batch measurement """
        commands = ["CONF:FREQ (@%s)" %(channel),
                    "TRIG:SOUR BUS",
                    "SAMPLE:COUNT %d" %(count),
                    "SENS:FREQ:MODE CONT",
                    "SENS:FREQ:GATE:TIME %g" %(gatetime),
                    "SENS:FREQ:GATE:SOUR TIME",
                    "CALC:STAT OFF",
                    ]
        for cmd in commands:
            self.device.write(cmd)

    def setupAllan(self, channel=1, gatetime=1, counts=30):
        commands = ["CONF:FREQ (@%s)" %(channel),
                    "TRIG:COUN 1",
                    "SAMP:COUN %s" %(counts),
                    "SENS:FREQ:MODE CONT",
                    "SENS:FREQ:GATE:TIME %g" %(gatetime),
                    "CALC:STAT ON",
                    "CALC:AVER:STAT ON"]
        for cmd in commands:
            self.device.write(cmd)

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)

    def initMeasure(self):
        ''' Init (trigger) measurement '''
        self.device.write("INIT")

    def getFreq(self):
        return float(self.device.ask("FETCH:FREQ?"))

    # def interrupt(self, intr):
    #     print visa.assert_interrupt_signal(intr)

    def parse(self, data):
        """
        Parsing format returned by R?
        From manual page 238
        """
        digits = int(data[1])
        chars = int(data[2:2+digits])
        start, stop = digits+2, digits+2+chars
        try:
            # Float has some rounding in the 16-17th digit or so...
            freqs = [float(f) for f in data[start:stop].split(',')]
        except (ValueError):
            freqs = []
        return freqs

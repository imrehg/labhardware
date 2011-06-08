import visa
from re import match

class StanfordSR830:
    sensunits = ["nV/fA", "uV/pA", "mV/nA", "V/uA"]
    sensuval = [1, 2, 5]
    timeunits = ["us", "ms", "s", "ks"]
    timeuval = [1, 3]

    def __init__(self, gpib):
        ''' Initialize device '''
        error = False
        self.__type = "lock-in amplifier"
        try:
            self.device = visa.instrument("GPIB::%d" %(gpib))
            if not self.__TestConnection():
                error = True
        except visa.VisaIOError:
            error = True

        if error:
            print "Exception: No %s on this gpib channel: %d" %(self.__type, gpib)
            return None
        else:
            print "Success: %s found" %(self.__type)

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        if (match(".*,SR830,.*", id)):
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

    def setupFast(self):
        ''' Set up parameters for fast measurement
        This follows the Programming Guide example,
        except trying to keep the precision higher
        '''
        self.device.write(":FORMAT:ASCII")
        self.device.write(":EVENT1:LEVEL 0")
        self.device.write(":DISP:ENAB OFF")
        # Turn off mathematics
        self.device.write(":CALC:MATH:STATE OFF")
        self.device.write(":CALC2:LIM:STATE OFF")
        self.device.write(":CALC3:AVER:STATE OFF")
        # Turn off printing
        self.device.write(":HCOPY:CONT OFF")
        # Redefine trigger
        self.device.write("*DDT #15FETC?")

    def setupGating(self, gatetime):
        self.device.write(":FREQ:ARM:STAR:SOUR IMM")
        self.device.write(":FREQ:ARM:STOP:SOUR TIM")
        self.device.write(":FREQ:ARM:STOP:TIM %f" %(gatetime))

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

    def getSensitivity(self):
        """ Get Sensitivity setting, using data from manual, algorithmically """
        sens = self.device.ask("SENS?")
        sensrange = self.sensunit[(sens + 1) / 9]
        value = self.sensuval[((sens+1)%9)%3] * 10**(((sens+1)%9) / 3)
        return (value, sensrange)

    def getTimeconstant(self):
        """ Get time constant setting, using data from the manual, algorithmically """
        olft = self.device.ask("OLFT?")
        timeunit = self.timeunits[(olft + 2) / 6]
        value = self.timeuval[((sens+2)%6)%2] * 10**(((sens+2)%6) / 2)
        return (value, timeunit)

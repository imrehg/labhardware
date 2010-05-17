import visa
from re import match

class Agilent8644:

    def __init__(self, gpib):
        ''' Initialize device '''
        self.device = visa.instrument("GPIB::%d" %(gpib))
        if (not self.__TestConnection()):
            print "No synthetizer on this gpib channel..."
            return None
        else:
            print "Synthetitzer found"

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        if (match(".*,8644B,.*", id)):
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

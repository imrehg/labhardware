import visa
from re import match

class AgilentMultimeter:

    def __init__(self, gpib):
        ''' Initialize device '''
        self.device = visa.instrument("GPIB::%d" %(gpib))
        if (not self.__TestConnection()):
            print "No multimeter on this GPIB channel..."
            return None
        else:
            print "Multimeter found"

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        if (match(".*,34401A,.*", id)):
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

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)

    def getDCVoltage(self, vrange, vresolution):
        ''' Get measurement of voltage in the defined range and resolution.
        These values will be changed by the counter to fit correct settings
        '''
        return float(self.device.ask("MEASURE:VOLTAGE:DC? %fV, %fV"
            %(vrange, vresolution)))

import visa
from re import match

class Agilent81150:

    def __init__(self, gpib):
        ''' Initialize device '''
        self.device = visa.instrument("GPIB::%d" %(gpib))
        if (not self.__TestConnection()):
            print "No function generator on this GPIB channel..."
            return None
        else:
            print "Function generator found"

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        if (match(".*,81150A,.*", id)):
            found = True
        else:
            found = False
        return found

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)



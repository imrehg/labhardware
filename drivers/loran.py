import visa
from re import match

class FS700:
    """ Stanford Research FS700 LORAN-C Frequency Standard """

    def __init__(self, gpib):
        ''' Initialize device '''
        self.device = visa.instrument("GPIB::%d" %(gpib))
        if (not self.__TestConnection()):
            print "No frequency standard on this GPIB channel..."
            return None
        else:
            print "Frequency standard found"

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        print id
        if (match(".*,FS700,.*", id)):
            found = True
        else:
            found = False
        return found

    def reset(self):
        ''' Reset and clear device '''
        pass

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)

    def startacq(self, GRI):
        self.write("STOP")
        self.write("GRIP %d" %(GRI))
        self.write("STTN -1")
        self.write("STRT")

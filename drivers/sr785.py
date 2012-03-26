import visa
from re import match

class StanfordSR785:

    def __init__(self, gpib):
        ''' Initialize device '''
        error = False
        self.__type = "dynamic signal analyzer"
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
        if (match(".*,SR785,.*", id)):
            found = True
        else:
            found = False
        return found

    def reset(self):
        ''' Reset and clear device '''
        self.device.write("*RST")
        self.device.write("*CLS")

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)


if __name__ == "__main__":
    device = StanfordSR785(10)

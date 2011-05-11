import visa
from re import match

class SMA100A:

    def __init__(self, gpib):
        ''' Initialize device '''
        error = False
        self.__type = "signal generator"
        try:
            self.device = visa.instrument("GPIB::%d" %(gpib))
            if not self.__TestConnection():
                error = True            
        except visa.VisaIOError:
            error = True
        
        if error:
            print "Exception: No %s on this gpib channel..." %(self.__type)
            return None
        else:
            print "Success: %s found" %(self.__type)

    def __TestConnection(self):
        ''' Test if we have the right device by matching id number '''
        id = self.device.ask("*IDN?")
        found = True if (match("SML", id)) else False
        return found

    def reset(self, oscref="INT"):
        ''' Reset and clear device '''
        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write(":SOUR:ROSC:SOUR %s" %oscref)
        self.device.write("SYST:PRES; *OPC?")
        return self.device.ask("SYST:SERR?")

    def write(self, command):
        ''' Connect to VISA write '''
        self.device.write(command)

    def read(self):
        ''' Connect to VISA read '''
        return self.device.read()

    def ask(self, command):
        ''' Connect to VISA ask '''
        return self.device.ask(command)

    def setFrequency(self, freq):
        self.device.write(":FREQ:CW %.2f hz" %(freq))

    def setPower(self, rfpower):
        self.device.write(":POW %.2f" %(rfpower))

    def rfoff(self):
        self.device.write("OUTP OFF")

    def rfon(self):
        self.device.write("OUTP ON")

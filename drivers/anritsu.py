"""
Drivers for Anritsu products
"""
import visa
from re import match
from numpy import array, append, linspace

class MS2601:
    """ Spectrum analyzer, old instrument.
    Please plug in GPIB before turning the instrument on

    """

    def __init__(self, gpib):
        """ Get an MS2601 device
        Input parameter: GPIB address (integer)

        """
        self.__type = "spectrum analyzer"

        # Be nice and try to interpret GPIB address
        if type(gpib) is not int:
            try:
                gpib = int(gpib)
            except ValueError:
                raise IOError("Can't understand GPIB address")

        error = False
        try:
            # Needs terminator char, manual section 10-12
            self.device = visa.instrument("GPIB::%d::INSTR" %(gpib), term_chars = visa.CR+visa.LF)
        except visa.VisaIOError:
            error = True

        if error:
            raise IOError("Exception: No %s on this gpib channel: %d" %(self.__type, gpib))
        else:
            print "Success: %s found" %(self.__type)

    def reset(self):
        ''' Reset and clear device '''
        self.device.write("INI")

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
    device = MS2601(18)
    device.reset()
    device.write("CNF 150MZ; SPF 10MZ")
    print device.ask("CNF?")
    print device.ask("SPF?")

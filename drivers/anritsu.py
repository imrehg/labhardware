"""
Drivers for Anritsu products
"""
import visa
from re import match
from numpy import array, append, linspace, zeros, sqrt
import struct

class MS2601:
    """ Spectrum analyzer, old instrument.
    Please plug in GPIB before turning the instrument on

    """

    units = {"UNT 0": "dBm",
             "UNT 1": "dBuV",
             "UNT 2": "dBmV",
             "UNT 3": "V",
             "UNT 4": "dBuV(emf)",
             "UNT 5": "dBuV/m",
             }

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

    def __dataconv(self, line):
        num = float(line[1:])
        if line[0] == '-':
            num *= -1
        return num

    def getunit(self):
        """ Get Y-unit of the currently set interface

        """
        unit = self.ask("UNT?")
        try:
            out = self.units[unit]
        except KeyError:
            out = None
        return out

    def getdata(self, start=None, num=None, binary=True):
        """ Transfer data from spectrum analyzer

        input parameters:
        start: start bin, integer (0 to 500), defaults to 0
        num: number of bins (1 to 501-start), defaults to 501
        binary: binary transfer (True/False), defaults to True

        return:
        resp: the response y values (dBm always)
        unit: fixed to dBm at the moment

        """
        start = 0 if not start else start
        num = 501 if not num else num
        resp = zeros(num)
        if binary:
            self.device.write("BIN 1")
            self.device.write("XMA? %d,%d" %(start, num))
            self.device.values_format = visa.double
            self.device.term_chars = ''
            res = self.read()
            for i in range(num):
                idx = i*2 + 1
                resp[i] = struct.unpack( "h", res[idx:idx+2] )[0] * 0.01
            self.device.values_format = visa.ascii
            self.device.term_chars = visa.CR+visa.LF
        else:
            self.device.write("BIN 0")
            self.device.write("XMA? %d,%d" %(start, num))
            for i in range(num):
                resp[i] = self.__dataconv(self.device.read())
        unit = self.units["UNT 0"]  # readout always seems to be in dBm, even if the interface is changed
        return resp, unit

    def dBmToV(self, dBm):
        """ Convert dBm into voltage value
        reference: http://www.referencedesigner.com/rfcal/cal_02.php

        """
        return sqrt(10 ** (dBm / 10) * (50 * 1e-3))

if __name__ == "__main__":
    device = MS2601(18)
    device.reset()
    device.write("CNF 150MZ; SPF 10MZ")
    print device.ask("CNF?")
    print device.ask("SPF?")

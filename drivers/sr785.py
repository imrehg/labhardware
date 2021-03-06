import visa
from re import match
from numpy import array, append

class StanfordSR785:

    def __init__(self, gpib):
        ''' Initialize device '''
        error = False
        self.__type = "dynamic signal analyzer"
        try:
            # Needs terminator char, manual p422
            self.device = visa.instrument("GPIB::%d" %(gpib), term_chars = visa.LF)
            if not self.__TestConnection():
                error = True
        except visa.VisaIOError:
            error = True

        if error:
            raise IOError("Exception: No %s on this gpib channel: %d" %(self.__type, gpib))
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

    def display_status_word(self, word):
        codes = ["NEWA",
                 "AVGA",
                 "STLA",
                 "LIMA",
                 "SSA",
                 "WFA",
                 "WFD",
                 "unused",
                 "NEWB",
                 "AVGB",
                 "STLB",
                 "LIMB",
                 "SSB",
                 "WFB",
                 "WFB",
                 "unused",
                 ]
        x = 1
        herecode = []
        for i in range(16):
            y = word & x
            if y > 0:
                herecode += [codes[i]]
            x = x << 1
        return bin(word), herecode

    def getdata(self, channel=2):
        if channel == 0 or channel == 2:
            data1 = [float(num) for num in self.ask("DSPY ? 0").split(',')]
            data1 = array(data1[0:-1])
        if channel == 1 or channel == 2:
            data2 = [float(num) for num in self.ask("DSPY ? 1").split(',')]
            data2 = array(data2[0:-1])

        if channel == 0:
            out = data1
        elif channel == 1:
            out = data2
        else:
            out = array(zip(data1, data2))
        return out

    def pulldata(self, chn=2):
        """
        Pull data from signal analyzer

        Input:
        ------
        chn: 0 - channel A, 1 - channel B, 2 - both A & B

        Currently assumes same length in display A and B
        """
        q = 1 if chn >= 1 else 0
        n = int(self.ask("DSPN ? %d" %(q)))

        datax = array([])
        for i in range(n):
            xi = float(self.ask("DBIN ? 0, %d" %i))
            datax = append(datax, xi)

        if chn == 0 or chn == 2:
            data1 = [float(num) for num in self.ask("DSPY ? 0").split(',')]
            data1 = array(data1[0:-1])
        if chn == 1 or chn == 2:
            data2 = [float(num) for num in self.ask("DSPY ? 1").split(',')]
            data2 = array(data2[0:-1])

        if chn == 0:
            out = array(zip(datax, data1))
        elif chn == 1:
            out = array(zip(datax, data2))
        else:
            out = array(zip(datax, data1, data2))
        return out


if __name__ == "__main__":
    import numpy as np
    from time import sleep
    import matplotlib
    matplotlib.rcParams['backend'] = 'wx'
    import matplotlib.pylab as pl

    device = StanfordSR785(18)
    # device.write("CLS; FSPN 0,200; STRT");
    # for i in range(40):
    #     print device.ask("DSPS?")
    #     sleep(1)
    start, stop = 1, 200
    device.write("SSTR 2, %d" %(start))
    device.write("SSTP 2, %d" %(stop))
    print device.ask("SSTR ? 0")
    print device.ask("SSTP ? 0")

    device.write("SRPT 2,0")

    device.ask("DSPS?")
    device.write("STRT")
    dataa, datab = False, False
    while not dataa or not datab:
        res = device.display_status_word(int(device.ask("DSPS ?")))
        print res
        codes = res[1]
        if 'SSA' in codes:
            dataa = True
        if 'SSB' in codes:
            datab = True
        # if dataa and datab:
        #     break
        sleep(1)

    # print device.ask("ACTD ?")
    # print device.ask("DTRD ? 2,0")
    # device.write("NOTE 0,1,0,50,50,Hello")
    # print device.ask("DUMP")
    data = [float(num) for num in device.ask("DSPY ? 0").split(',')]
    data = data[0:-1]
    pts = len(data)
    f = np.logspace(np.log10(start), np.log10(stop), pts) # this is incorrect
    pl.semilogx(f, data)
    pl.show()

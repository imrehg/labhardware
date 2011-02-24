"""
Allan variance logger for Agilent 53230A.
Some of the methods should only work with this model.
"""
from time import time, strftime, sleep
import numpy as np
import ConfigParser as cp
import sys
import re

from agilent53230 import Counter

if __name__ == "__main__":

    try:
        configfile = sys.argv[1]
        config = cp.ConfigParser()
        config.readfp(open(configfile))
    except:
        print "Cannot find configuration file."
        sys.exit(1)

    # Config settings
    countergpib = config.getint('Setup','counter_GPIB')

    # Setting up frequency counter
    counter = Counter(gpib = countergpib)
    if (counter == None):
        sys.exit(2)

    ### Include measurement section in config

    ch = int(raw_input("Channel number:  "))
    mintime = float(raw_input("Minimum gate time (s):  "))
    maxtime = float(raw_input("Maximum gate time (s):  "))
    steps = int(raw_input("Number of gate times:  "))
    counts = int(raw_input("Number of reading each:  "))

    gates = np.logspace(np.log10(mintime), np.log10(maxtime), steps)


    datafile = "allan_%s.log" %(strftime("%y%m%d_%H%M%S"))
    out = file(datafile, 'a')
    out.write("#Gatetime(s) AllanDev(Hz)\n")

    for gatetime in gates:

        start = time()        
        counter.setupAllan(channel=ch, gatetime=gatetime, counts=counts)
        counter.write("INIT")
        print "Averaging time: %g s" %(gatetime)

        if (gatetime*counts > 2):
            stoptime = start + gatetime*counts -1
            while time() < stoptime:
                try:
                    sleep(0.1)
                except KeyboardInterrupt:
                    out.close()
                    print "Interrupt by user"
                    sys.exit(1)
        
        allan = counter.write("*WAI")
        # Ask for the result, this also starts the next measurement
        allan = float(counter.ask("CALC:AVER:ADEV?"))
        print("Allan deviation: %g Hz" %(allan))
        result = np.array([[gatetime, allan]])
        np.savetxt(out, result)
    out.close()


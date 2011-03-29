"""
Allan variance logger for Agilent 53230A.
Some of the methods should only work with this model.
"""
from time import time, strftime, sleep
import numpy as np
import ConfigParser as cp
import sys
import re
import logging

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


    # Setup output file
    logger = logging.getLogger()
    logfile = config.get('Setup','logfile')
    if logfile == 'auto':
        logfile = "allan_%s.log" %(strftime("%y%m%d_%H%M%S"))
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # Write header
    logger.info("#Gatetime(s) AllanDev(Hz)")

    for gatetime in gates:

        start = time()
        counter.setupAllan(channel=ch, gatetime=gatetime, counts=counts)
        counter.write("INIT")
        print "Gating time: %g s" %(gatetime)

        if (gatetime*counts > 2):
            stoptime = start + gatetime*counts -1
            while time() < stoptime:
                try:
                    sleep(0.1)
                except KeyboardInterrupt:
                    print "Interrupt by user"
                    sys.exit(1)

        allan = counter.write("*WAI")
        # Ask for the result, this also starts the next measurement
        allan = float(counter.ask("CALC:AVER:ADEV?"))
        print("Allan deviation: %g Hz" %(allan))
        logger.info("%e,%e" %(gatetime, allan))

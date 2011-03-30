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
    logfile = "allan_%s.log" %(strftime("%y%m%d_%H%M%S"))
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # Write settings/data header
    logger.info("#Allan w/ Agilent 53230, settings:")
    settings = {'Channel number':ch,
                'Minimum gating time':mintime,
                'Maximum gating time':maxtime,
                'Number of gating times':steps,
                'Number of readings each:':counts,
                }
    for setting, value in settings.items():
        logger.info("#%s : %s" %(setting, value))
    logger.info("#Gatetime(s) AllanDev(Hz) AverageFq(Hz) MinFq(Hz) MaxFq(Hz)")

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
        avgfq = float(counter.ask("CALC:AVER:AVER?"))
        minfq = float(counter.ask("CALC:AVER:MIN?"))
        maxfq = float(counter.ask("CALC:AVER:MAX?"))
        print("Allan deviation: %g Hz" %(allan))
        logger.info("%e,%e,%.5f,%.5f,%.5f" %(gatetime, allan, avgfq, minfq, maxfq))

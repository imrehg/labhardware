"""
Allan variance logger for Agilent 53230A.
Some of the methods should only work with this model.

Continue logging until it's stopped
"""
from time import time, strftime, sleep
import numpy as np
import ConfigParser as cp
import sys
import re
import logging

sys.path.append("../../drivers")
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
    if counter is None:
        sys.exit(2)

    ### Include measurement section in config

    ch = int(raw_input("Channel number:  "))
    gate = float(raw_input("Gate time (s):  "))

    # Setup output file
    logger = logging.getLogger()
    logfile = "allanlong_%s.log" %(strftime("%y%m%d_%H%M%S"))
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # Write settings/data header
    logger.info("#Allan w/ Agilent 53230, settings:")
    settings = {'Channel number':ch,
                'Gate time':gate,
                }
    for setting, value in settings.items():
        logger.info("#%s : %s" %(setting, value))
    logger.info("#Time(Epoch) Frequency(Hz)")

    counter.setupFreq(channel=ch, gatetime=gate)
    while True:
        try:
            start = time()
            freq = counter.getFreq()
            print("Elapsed: %f" %(time()-start))
            print("Frequency: %g Hz" %(freq))
            logger.info("%.3f,%.5f" %(start, freq))
        except (KeyboardInterrupt):
            print "Interrupted by user"
            break

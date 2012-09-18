"""
Transfering data from Anritsu MS2601 spectrum analyzer
"""
from __future__ import division
import ConfigParser
import numpy as np
import sys
from time import strftime

## For Windows:
import matplotlib
matplotlib.rcParams['backend'] = 'wx'
import matplotlib.pylab as pl

# Own modules
sys.path.append("../../drivers/")
import anritsu

if __name__ == "__main__":

    # Load configuration
    try:
        configfile = sys.argv[1]  # first argument is configuration file name
        config = ConfigParser.ConfigParser()
        config.readfp(open(configfile))
    except:
        print "Cannot find configuration file."
        sys.exit(1)

    runparams = [None]
    if len(sys.argv) >= 2:
        try:
            runparams[0] = int(sys.argv[2])  # should be basename
        except (ValueError, IndexError):
            pass

    # Get Configuration
    GPIB = config.getint('Setup', 'GPIB')
    basename = config.get('Setup', 'Basename')

    # Connect to device
    try:
        device = anritsu.MS2601(GPIB)
    except (IOError):
        print("Couldn't find things on GPIB channel %d, exiting" %(GPIB))
        sys.exit(1)

    # Setting up the output filename
    if not runparams[0]:
        name = raw_input("Output basename? (default: %s) " %basename)
        if len(name) > 0:
            basename = name
    else:
        basename = runparams[3]
    outname = "%s_%s" %(basename, strftime("%y%m%d_%H%M%S"))

    cnf = int(device.ask("CNF?")[3:])
    spf = int(device.ask("SPF?")[3:])
    freq = np.linspace(cnf - spf/2, cnf + spf/2, 501)
    
    receive = device.getdata()
    vals = np.array(zip(freq, receive))

    np.savetxt("%s.csv" %(outname), vals, delimiter=",")

    pl.plot(vals[:, 0]/1e6, vals[:, 1])
    pl.xlabel("Frequency (MHz)")
    pl.ylabel("Spectrum (dBV)")
    pl.savefig("%s.png" %(outname))

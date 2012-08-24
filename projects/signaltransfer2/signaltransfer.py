"""
Transfering data from Stanford Research SR785 Signal analyzer
"""
import ConfigParser
import numpy as np
import sys
from time import strftime

## For Windows:
import matplotlib
matplotlib.rcParams['backend'] = 'wx'
import matplotlib.pylab as pl

# Own modules
sys.path.append("../../")
sys.path.append("../../drivers/")
import sr760

if __name__ == "__main__":

    # Load configuration
    try:
        configfile = sys.argv[1]  # first argument is configuration file name
        config = ConfigParser.ConfigParser()
        config.readfp(open(configfile))
    except:
        print "Cannot find configuration file."
        sys.exit(1)

    # Get Configuration
    GPIB = config.getint('Setup', 'GPIB')
    basename = config.get('Setup', 'Basename')
    outname = "%s_%s" %(basename, strftime("%y%m%d_%H%M%S"))

    # Connect to device
    try:
        device = sr760.StanfordSR760(GPIB)
    except (IOError):
        print("Couldn't find things on GPIB channel %d, exiting" %(GPIB))
        sys.exit(1)

    # # Check which channels to download
    # chnget = -1
    # while chnget not in range(3):
    #     try:
    #         chnget = int(raw_input("Which views to get? 0: view A, 1: view B, 2: both view A&B : "))
    #     except(ValueError):
    #         pass

    # Get data and save
    vals = device.pulldata()
    np.savetxt("%s.csv" %(outname), vals, delimiter=",")

    # Data plotting
    xval = vals[:, 0]
    pl.figure(figsize=(11.69, 8.27))  # landscape alignment A4
    yval = vals[:, 1]
    pl.subplot(111)
    pl.plot(xval, yval, '-')
    pl.ylabel('Y')
    pl.xlabel('Hz')
    pl.xlim([xval[0], xval[-1]])
    pl.savefig("%s.png" %(outname))

    device.write("LOCL 0")

    pl.show()

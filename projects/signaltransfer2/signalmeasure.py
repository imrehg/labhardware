"""
Transfering data from Stanford Research SR785 Signal analyzer
"""
import ConfigParser
import numpy as np
import sys
from time import strftime, sleep

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

    print "0: 191mHz\t1: 382mHz\t2:763mHz\t3:1.5Hz"
    print "4: 3.1Hz\t5: 6.1Hz\t6: 12.2Hz\t7: 24.4Hz"
    print "8: 48.75Hz\t9: 97.5Hz\t19: 195Hz\t11: 390Hz"
    print "12: 780Hz\t13: 1.56kHz\t14: 3.125kHz\t15: 6.25kHz"
    print "16: 12.5kHz\t17: 25kHz\t18: 50kHz\t19: 100kHz"

    span = -1
    while span not in range(20):
        try:
            span = int(raw_input("Frequency span? (s = 0-19) "))
        except ValueError:
            pass

    if span == 0:
        multiplier = 0
    else:
        multiplier = -1
    while multiplier not in range(span+1):
        try:
            multiplier = int(raw_input("Multiplier? (m = 0-%d), meaning 2^m better resolution " %(span)))
        except ValueError:
            pass

    realspan = span - multiplier
    ranges = 2 ** multiplier
    
    device.write("SPAN %d" %(realspan))
    startfreq = 0
    basefreq = device.basefreq
    freqstep = basefreq / 2**(19 - realspan)
    for i in range(ranges):
        device.write("STRF %f" %(startfreq))
        device.write("AVGO 1")
        device.write("NAVG 200")
        device.write("AVGT 0")
        device.write("AVGM 0")
        device.write("OVLP 0")
        sleep(0.05)
        device.write("STRT")
        sleep(0.05)
        ready = False
        while not ready:
            val = int(device.ask('*STB?'))
            ready = (val & 1)
            sleep(0.1)
        data = device.pulldata()
        if i == 0:
            vals = data
        else:
            vals = np.append(vals, data, axis=0)
        print "Done %d/%d" %(i+1, ranges)
        startfreq += freqstep

    # Get save data
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

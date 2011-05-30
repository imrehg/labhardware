from __future__ import division
from time import sleep, strftime
import ConfigParser
import logging
import numpy
import sys

# Device drivers
import sma100a
import stanfordSR830

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Initial setup
siggen = sma100a.SMA100A(config.getint('Setup','siggen_GPIB'))
lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))

siggen.rfoff()
# Enforce external reference
result = siggen.reset("EXT")
print "Reset result: %s" %(result)

## Get settings from config file
# Signal generator
eomcenter = config.getfloat('Experiment', 'freqcenter')
eomscan = [config.getfloat('Experiment', 'scanstart'),
           config.getfloat('Experiment', 'scanstop')]
eomscansteps = config.getint('Experiment', 'scansteps')
rfpower = config.getfloat('Experiment', 'rfpower')
lffreq = config.getfloat('Experiment', 'lffreq')
fmdev = config.getfloat('Experiment', 'fmdev')

# Lockin amplifier
# Check Manual for the meaning of these integers: pages 5-13 and 5-6
lockinsensitivity = config.getint('Experiment','lockinsensitivity')
lockinrate = config.getint('Experiment','lockinrate')
lockintimeconstant = config.getint('Experiment','lockintimeconstant')
startdelay = config.getfloat('Experiment','startdelay')
lockinch1 = config.getfloat('Experiment','lockinch1')
lockinch2 = config.getfloat('Experiment','lockinch2')
repeats = config.getint('Experiment','repeats')

if lockinch1 == 0:
    ch1name = "Xcurrent(A)"
elif lockinch1 == 1:
    ch1name = "Rcurrent(A)"
else:
    ch1name = "Ch1/Choice%d" %lockinch1

if lockinch2 == 0:
    ch2name = "Ycurrent(A)"
elif lockinch2 == 1:
    ch2name = "PhaseAngle(Deg)"
else:
    ch2name = "Ch2/Choice%d" %lockinch2

# Setup logging
logger = logging.getLogger()
logfile = config.get('Setup','logfile')
if logfile == 'auto':
    logfile = "gigahertz_%s.log" %(strftime("%y%m%d_%H%M%S"))
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 

# Save configuration info
f = open(configfile)
for line in f:
    logger.info("# %s" %line.strip())
f.close()

# Setting up the experiment with FM modulation
siggen.write(":SOUR:MODE CW")
siggen.setFrequency(eomcenter + eomscan[0])
siggen.setPower(rfpower)
siggen.write(":LFO:FREQ %.1f" %(lffreq))
siggen.write(":LFO:FREQ:MODE CW")
siggen.write(":LFO ON")
siggen.write(":FM:DEV %.1f" %(fmdev))
siggen.write(":FM:STAT ON")
siggen.rfon()
siggen.write("*OPC?")

# Setup lock-in amplifier to get a number of datapoints in one go
lockin.write("REST")
lockin.write("SRAT %d" %(lockinrate))
lockin.write("OFLT %d" %(lockintimeconstant))
lockin.write("SENS %d" %(lockinsensitivity))
lockin.write("DDEF1,%d,0" %(lockinch1))
lockin.write("DDEF2,%d,0" %(lockinch2))
# q = ["SRAT?", "SPTS?", "SEND?", "OFLT?", "SENS?"]
# for quest in q:
#     print quest, "->", lockin.ask(quest)

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#EOMFrequency(Hz) %s %s" %(ch1name, ch2name))

ss = numpy.linspace(eomscan[0], eomscan[1], eomscansteps)
print "Frequency center: %.2f Hz" %(eomcenter)
for index, scanning in enumerate(ss):
    print "Detuning %d / %d: %.2f Hz" %(index+1, eomscansteps, scanning) 

    # Set and read back function generator frequency for scanning
    siggen.setFrequency(eomcenter+scanning)
    setfreq = float(siggen.ask(":FREQ?")) - eomcenter

    sleep(startdelay)
    # Lock-in amplifier measurement
    lockin.write("REST")
    lockin.write("STRT")
    # Wait until there's enough data
    while (int(lockin.ask("SPTS?")) < repeats):
        try:
            sleep(0.01)
        except KeyboardInterrupt:
            # Wanna shut down data collection
            lockin.write("PAUS")
            sys.exit(0)

    lockin.write("PAUS")
    tempch1 = lockin.ask("TRCA?1,0,%d" %(repeats))
    tempoutch1 = numpy.array([float(x) for x in tempch1.split(',') if not (x == '')])
    tempch2 = lockin.ask("TRCA?2,0,%d" %(repeats))
    tempoutch2 = numpy.array([float(x) for x in tempch2.split(',') if not (x == '')])

    for index in xrange(repeats):
        logger.info("%.3f,%e,%e" %(setfreq, tempoutch1[index], tempoutch2[index]))

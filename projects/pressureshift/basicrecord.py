from __future__ import division

from time import sleep, strftime
from numpy import *
import ConfigParser
import sys
import logging
 
import agilent81150
import agilentcounter
import stanfordSR830


try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

def checklock(beatfreq, setfreq):
    """ Panic switch if unlocked laser is detected """
    # if abs(abs(setfreq) - beatfreq) > 1000:
    #     print "Unlocked!"
    #     sys.exit(1)
    pass


# Import configuration and do basic setup
funcgen = agilent81150.Agilent81150(config.getint('Setup','funcgen_GPIB'))
#counter = agilentcounter.AgilentCounter(config.getint('Setup','counter_GPIB'))
lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))

try:
    lockin2_GPIB = config.getint('Setup', 'lockin2_GPIB')
    lockin2 = stanfordSR830.StanfordSR830(lockin2_GPIB)
except:
    lockin2 = None


# Get settings from config file
aomcentre = config.getfloat('Experiment','aomcentre')
aomamp = [config.getfloat('Experiment', 'aomamplitude1'),
          config.getfloat('Experiment', 'aomamplitude2')]
aomscan = [config.getfloat('Experiment','scanstart'),
           config.getfloat('Experiment','scanstop')]
aomscansteps = config.getint('Experiment','scansteps')
repeats = config.getint('Experiment','repeats')
amchannel = config.getint('Experiment','amchannel')
amdepth = config.getint('Experiment', 'amdepth')
amfrequency = config.getfloat('Experiment','amfrequency')
countergate = config.getfloat('Experiment','countergate')
# Check Manual for the meaning of these integers: pages 5-13 and 5-6
lockinsensitivity = config.getint('Experiment','lockinsensitivity')
lockinrate = config.getint('Experiment','lockinrate')
lockintimeconstant = config.getint('Experiment','lockintimeconstant')
startdelay = config.getfloat('Experiment','startdelay')
lockinch1 = config.getfloat('Experiment','lockinch1')
lockinch2 = config.getfloat('Experiment','lockinch2')

# Setup logging
logger = logging.getLogger()
logfile = config.get('Setup','logfile')
if logfile == 'auto':
    logfile = "pressureshift_%s.log" %(strftime("%y%m%d_%H%M%S"))
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


# Setup instruments
# Function generator
#funcgen.write(":FREQ1 %f" %(aomcentre))
#funcgen.write(":VOLTAGE1:AMPLITUDE %fmVpp" %(aomamp[0]))
funcgen.write(":FREQ2 %f" %(aomcentre))
funcgen.write(":VOLTAGE2:AMPLITUDE %fmVpp" %(aomamp[1]))
funcgen.write(":AM%d:DEPTH %dPCT" %(amchannel, amdepth))
funcgen.write(":AM%d:INT:FREQUENCY %f" %(amchannel, amfrequency))
funcgen.write(":AM%d:STATE On" %(amchannel))
# # Frequency counter
# counter.reset()
# counter.setupFast()
# counter.setupGating(countergate)
# Lock-in amplifier
lockin.write("REST")
lockin.write("SRAT %d" %(lockinrate))
lockin.write("OFLT %d" %(lockintimeconstant))
lockin.write("SENS %d" %(lockinsensitivity))
lockin.write("DDEF1,%d,0" %(lockinch1))
lockin.write("DDEF2,%d,0" %(lockinch2))

q = ["SRAT?", "SPTS?", "SEND?", "OFLT?", "SENS?"]
for quest in q:
    print quest, "->", lockin.ask(quest)

## Second lock-in data log
if lockin2:
    ## OLFT: Time constant
    ## SENS: Sensitivity
    logging.info("# Frequency stabilization lockin: ")
    sens = lockin2.getSensitivity()
    logging.info("# Sensitivity: %d %s" %(sens[0], sens[1]))
    tconst = lockin2.getTimeconstant()
    logging.info("# Time constant: %d %s" %(tconst[0], tconst[1]))


print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#AOMFrequency(Hz) MeasuredBeat(Hz) LockInSignal(V)")

ss = linspace(aomscan[0],aomscan[1],aomscansteps)
for index, scanning in enumerate(ss):

    print "Detuning %d / %d: %f Hz" %(index+1, aomscansteps, scanning) 

    # Set and read back function generator frequency for scanning
    funcgen.write(":FREQ%d %f" %(amchannel, aomcentre+scanning))
    setfreq = float(funcgen.ask(":FREQ%d?" %(amchannel))) - aomcentre
    sleep(startdelay)

    # # Counter 
    # counter.initMeasure()

    # Lock-in amplifier measurement
    lockin.write("REST")
    lockin.write("STRT")
    # Wait until there's enough data
    while (int(lockin.ask("SPTS?")) < repeats):
        sleep(0.2)
    lockin.write("PAUS")
    tempch1 = lockin.ask("TRCA?1,0,%d" %(repeats))
    tempoutch1 = array([float(x) for x in tempch1.split(',') if not (x == '')])
    tempch2 = lockin.ask("TRCA?2,0,%d" %(repeats))
    tempoutch2 = array([float(x) for x in tempch2.split(',') if not (x == '')])

    # beatfreq = counter.getFreq()

    # checklock(beatfreq, setfreq)

    for index in xrange(repeats):
#        logger.info("%.3f,%.3f,%e,%e" %(setfreq, beatfreq, tempoutch1[index], tempoutch2[index]))
        logger.info("%.3f,%e,%e" %(setfreq, tempoutch1[index], tempoutch2[index]))

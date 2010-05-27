from __future__ import division

from time import sleep, strftime
from numpy import *
import ConfigParser
import sys
import logging
 
import agilent8644
import stanfordSR830

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Import configuration and do basic setup
synth = agilent8644.Agilent8644(config.getint('Setup','synth_GPIB'))
lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))
synthdivider = config.getint('Setup','synthdivider')

clock =  config.getfloat('Setup','clock')
clockscan = [config.getfloat('Experiment','scanstart'),
             config.getfloat('Experiment','scanstop')]
scansteps = config.getint('Experiment','scansteps')
repeats = config.getint('Experiment','repeats')
# Check Manual for the meaning of these integers: pages 5-13 and 5-6
lockinsensitivity = config.getint('Experiment','lockinsensitivity')
lockinrate = config.getint('Experiment','lockinrate')
lockintimeconstant = config.getint('Experiment','lockintimeconstant')
startdelay = config.getfloat('Experiment','startdelay')
lockinch1 = config.getfloat('Experiment','lockinch1')
lockinch2 = config.getfloat('Experiment','lockinch2')

logger = logging.getLogger()
logfile = config.get('Setup','logfile')
if logfile == 'auto':
    logfile = "cpt_%s.log" %(strftime("%y%m%d_%H%M%S"))
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

synth.write("FREQ:CW %f HZ" %(clock/synthdivider))

q = ["FREQ:CW?"]
for quest in q:
    print quest, "->", synth.ask(quest)

lockin.write("REST")
lockin.write("SRAT %d" %(lockinrate))
lockin.write("OFLT %d" %(lockintimeconstant))
lockin.write("SENS %d" %(lockinsensitivity))
lockin.write("DDEF1,%d,0" %(lockinch1))
lockin.write("DDEF2,%d,0" %(lockinch2))

lockin.write("FAST 0")
q = ["SRAT?", "SPTS?", "SEND?", "OFLT?", "SENS?"]
for quest in q:
    print quest, "->", lockin.ask(quest)

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#AimedClockFrequency(Hz) LockInSignal(V)")

ss = linspace(clockscan[0],clockscan[1],scansteps)
for index, scanning in enumerate(ss):
    freq = clock + scanning
    print "Detuning %d / %d: %f Hz" %(index+1, scansteps, scanning) 
    synth.write("FREQ:CW %f HZ" %(freq/synthdivider))
    # Let it settle
    sleep(startdelay)
    lockin.write("REST")
    lockin.write("STRT")
    # Wait until there's enough data
    while (int(lockin.ask("SPTS?")) < repeats):
        sleep(0.5)
    lockin.write("PAUS")
    tempch1 = lockin.ask("TRCA?1,0,%d" %(repeats))
    tempoutch1 = array([float(x) for x in tempch1.split(',') if not (x == '')])
    tempch2 = lockin.ask("TRCA?2,0,%d" %(repeats))
    tempoutch2 = array([float(x) for x in tempch2.split(',') if not (x == '')])
    for index in xrange(repeats):
        logger.info("%1.3f,%e,%e" %(freq, tempoutch1[index], tempoutch2[index]))

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
lockinrate = config.getint('Experiment','lockinrate')

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
lockin.write("FAST 0")
q = ["SRAT?", "SPTS?", "SEND?"]
for quest in q:
    print quest, "->", lockin.ask(quest)

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#AimedClockFrequency(Hz) LockInSignal(V)")

ss = linspace(clockscan[0],clockscan[1],scansteps)
results = zeros((scansteps, 2))
for index, scanning in enumerate(ss):
    freq = clock + scanning
    print "Detuning %d / %d: %f Hz" %(index+1, scansteps, scanning) 
    synth.write("FREQ:CW %f HZ" %(freq/synthdivider))
    # Let it settle
    sleep(1)
    lockin.write("REST")
    lockin.write("STRT")
    # Wait until there's enough data
    while (int(lockin.ask("SPTS?")) < repeats):
        sleep(0.5)
    lockin.write("PAUS")
    temp = lockin.ask("TRCA?1,0,%d" %(repeats))
    temp2 = array([float(x) for x in temp.split(',')[0:-1]])
    results[index, 0:2] = [freq, average(temp2)]
    for measure in temp2:
        logger.info("%1.3f,%e" %(freq, measure))

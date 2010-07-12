from __future__ import division

from time import sleep, strftime, time
from numpy import *
import ConfigParser
import sys
import logging
 
import agilent81150
import powermeter

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Import configuration and do basic setup
funcgen = agilent81150.Agilent81150(config.getint('Setup','funcgen_GPIB'))
meter = powermeter.PowerMeter() 

# Get settings from config file
aomcentre = config.getfloat('Experiment','aomcentre')
aomscan = [config.getfloat('Experiment','scanstart'),
           config.getfloat('Experiment','scanstop')]
aomscansteps = config.getint('Experiment','scansteps')
amchannel = config.getint('Experiment','amchannel')
tstep  = config.getfloat('Experiment','timestep')
repeats = config.getint('Experiment','repeats')

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
# funcgen.write(":AM%d:DEPTH %dPCT" %(amchannel, amdepth))
# funcgen.write(":AM%d:INT:FUNC SQU" %(amchannel))
# funcgen.write(":AM%d:INT:FREQUENCY %f" %(amchannel, amfrequency))
# funcgen.write(":AM%d:STATE On" %(amchannel))
# # Frequency counter
# counter.reset()
# counter.setupFast()
# counter.setupGating(countergate)
# Lock-in amplifier

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#AOMFrequency(Hz) Powermeter(W)")

ss = linspace(aomscan[0],aomscan[1],aomscansteps)

start = time()
for index, scanning in enumerate(ss):

    print "Detuning %d / %d: %f Hz" %(index+1, aomscansteps, scanning) 

    # Set and read back function generator frequency for scanning
    funcgen.write(":FREQ%d %f" %(amchannel, aomcentre+scanning))
    setfreq = float(funcgen.ask(":FREQ%d?" %(amchannel))) - aomcentre

    reps = 0
    while True:
        if (time() - start < tstep):
            continue
        now = time()
        fvalue = meter.getReading()
        # Sometimes the powermeter fails to answer, don't fail for that...
        if fvalue is None:
            continue
        print "%.3fs -> %e W" %((now-start), fvalue)
        logger.info("%.3f,%e" %(setfreq, fvalue))
        start = now
        reps += 1
        if reps == repeats:
            break
        

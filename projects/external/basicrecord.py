from __future__ import division

from time import sleep, strftime, clock
from numpy import *
import ConfigParser
import sys
import logging
 
import agilentawg
import agilentcounter
import agilentmultimeter

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Connect to equipment
funcgen = agilentawg.AgilentAWG(config.getint('Setup','funcgen_GPIB'))
multi = agilentmultimeter.AgilentMultimeter(config.getint('Setup','multimeter_GPIB'))
counter = agilentcounter.AgilentCounter(config.getint('Setup','counter_GPIB'))

# Import configuration and do basic setup
vrange = config.getint('Experiment', 'voltagerange')
countergating = config.getfloat('Experiment', 'countergating')
pztscan = [config.getfloat('Experiment','scanstart'),
             config.getfloat('Experiment','scanstop')]
scansteps = config.getint('Experiment','scansteps')
# repeats = config.getint('Experiment','repeats')
startdelay = config.getfloat('Experiment','startdelay')

# Setup output file
logger = logging.getLogger()
logfile = config.get('Setup','logfile')
if logfile == 'auto':
    logfile = "external_%s.log" %(strftime("%y%m%d_%H%M%S"))
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

######### Setup equipment
### COUNTER
counter.reset()
counter.setupFast()
counter.write(":FUNC 'FREQ 1'")
counter.setupGating(countergating)

# Setting up multimeter
multi.reset()
# 5-1/2 digits fast
multi.write("CONF:VOLT:DC %d" %(vrange))
multi.write("VOLT:DC:NPLC 0.2")
multi.write("TRIG:SOUR IMM")
# Need to do one reading to set up Wait-For-Trigger state!
multi.ask("READ?")

multi.write("SAMPLE:COUNT 1")

# ### Measurement cycle
# - start counter, it has ~50ms dead time in the beginning (?)
# - delay to overlap multimeter and counter
# - start multimeter measurement (currently about 10ms for readout)
# - read out counter
# ==> this hopefully overlaps the two measurements, if the dead time is mostly in the beginning of interval

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
logging.info("#PZT_voltage(V) BeatFrequency(HZ) PMT_voltage(V)")

ss = linspace(pztscan[0],pztscan[1],scansteps)
for index, scanning in enumerate(ss):

    funcgen.write("VOLTAGE:OFFSET %f" %scanning)
    print "PZT voltage %d / %d: %f V" %(index+1, scansteps, scanning) 
    sleep(startdelay)
    # Start frequency counter
    counter.write(":INIT;")
    start = clock()
    sleep(0.035)
    v = multi.ask("READ?")
    counter.ask("*OPC?")
    # print clock() - start
    f = counter.ask("FETCH:FREQ?")
    voltage = float(v)
    frequency = float(f)
    logger.info("%f,%e,%e" %(scanning, frequency, voltage))

from __future__ import division

from time import sleep, strftime
from numpy import *
import sys
import logging
import nidaqmx

try:
    import configparser as ConfigParser
except ImportError:
    import Configparser

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Connect to equipment
daqdevice = config.get('Setup','deviceID')
transch = config.get('Setup','transchID')
fluoch = config.get('Setup','fluochID')
# Import configuration and do basic setup
synthdivider = config.getint('Setup','synthdivider')
clock =  config.getfloat('Setup','clock')
clockscan = [config.getfloat('Experiment','scanstart'),
             config.getfloat('Experiment','scanstop')]
scansteps = config.getint('Experiment','scansteps')
repeats = config.getint('Experiment','repeats')
measurefreq = config.getint('Experiment', 'measurefreq')
startdelay = config.getfloat('Experiment','startdelay')

# Setup output file
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

###################
# Tune the synthetizer to the starting point
synth.write("FREQ:CW %f HZ" %((clock+clockscan[0])/synthdivider))

# Query synthetizer settings
q = ["FREQ:CW?"]
for quest in q:
    print quest, "->", synth.ask(quest)

###############
# Setup DAQ channnels
measure = nidaqmx.AnalogInputTask()
measure.create_voltage_channel(['%s/%s' %(daqdevice, transch),
                                '%s/%s' %(daqdevice, fluoch)],
                               terminal = 'diff',
                               units='volts',
                               min_val=0,
                               max_val=10.0)
measure.configure_timing_sample_clock(rate = measurefreq,
                                      sample_mode = 'finite',
                                      samples_per_channel = repeats)


print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
reffreq = float(lockin.ask("FREQ?"))
logging.info("# Reference frequency: %f Hz" %reffreq)
logging.info("#AimedClockFrequency(Hz) Translight(V) Fluolight(V)")

####### Let's get to it
ss = linspace(clockscan[0],clockscan[1],scansteps)
for index, scanning in enumerate(ss):
    freq = clock + scanning
    print "Detuning %d / %d: %f Hz" %(index+1, scansteps, scanning) 
    synth.write("FREQ:CW %f HZ" %(freq/synthdivider))
    # Let things settle
    sleep(startdelay)

    measure.start()
    measure.wait_until_done(timeout=-1)
    data = measure.read(samples_per_channel=repeats,timeout=10,fill_mode='group_by_scan_number')

    print data
    for index in xrange(0, 2*repeat, 2):
        logger.info("%1.3f,%e,%e" %(freq, data[index], data[index+1]))

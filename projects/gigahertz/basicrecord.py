from __future__ import division
from time import sleep, strftime
import ConfigParser
import logging
import numpy
import sys
import sma100a

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Initial setup
siggen = sma100a.SMA100A(config.getint('Setup','GPIB'))
siggen.rfoff()
result = siggen.reset()
print "Reset result: %s" %(result)

# Get settings from config file
eomcenter = config.getfloat('Experiment', 'freqcenter')
eomscan = [config.getfloat('Experiment', 'scanstart'),
           config.getfloat('Experiment', 'scanstop')]
eomscansteps = config.getint('Experiment', 'scansteps')
rfpower = config.getfloat('Experiment', 'rfpower')
delay = config.getfloat('Experiment', 'delay')

# # Setup logging
# logger = logging.getLogger()
# logfile = config.get('Setup','logfile')
# if logfile == 'auto':
#     logfile = "gigahertz_%s.log" %(strftime("%y%m%d_%H%M%S"))
# hdlr = logging.FileHandler(logfile)
# formatter = logging.Formatter('%(message)s')
# hdlr.setFormatter(formatter)
# logger.addHandler(hdlr)
# logger.setLevel(logging.INFO) 

# # Save configuration info
# f = open(configfile)
# for line in f:
#     logger.info("# %s" %line.strip())
# f.close()

ss = numpy.linspace(eomscan[0], eomscan[1], eomscansteps)

siggen.setFrequency(eomcenter + ss[0])
siggen.setPower(rfpower)
siggen.rfon()

print "Frequency center: %.2f Hz" %(eomcenter)
for index, scanning in enumerate(ss):
    print "Detuning %d / %d: %.2f Hz" %(index+1, eomscansteps, scanning) 

    # Set and read back function generator frequency for scanning
    siggen.setFrequency(eomcenter+scanning)
    setfreq = float(siggen.ask(":FREQ?")) - eomcenter

    # This is not meant for synchronization...
    sleep(delay)


from nidaqmx import *
from time import strftime
import logging
import ConfigParser
import sys
from time import time

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Load settings
device = config.get('Setup', 'deviceID')
channel = config.get('Setup', 'channelID')
readrate = config.getfloat('Experiment', 'readrate')
saverate = config.getint('Experiment', 'saverate')

# Setup logging
logger = logging.getLogger()
# logfile = config.get('Setup','logfile')
logfile = 'auto'
if logfile == 'auto':
    logfile = "photodiode_%s.log" %(strftime("%y%m%d_%H%M%S"))
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

# Set up logging
task = AnalogInputTask()
task.create_voltage_channel('%s/%s' %(device, channel),
                            terminal = 'diff',
                            min_val=0,
                            max_val=10.0)
task.configure_timing_sample_clock(rate = readrate,
                                   sample_mode='continuous')

task.start()

start = time()
while True:
    try:
        data = task.read(saverate)
        for d in data:
            logger.info(d[0])
        print "%.0fs :: Written!" %(time()-start)
    except KeyboardInterrupt:
        del task
        print "Finished"


"""
Keep saving data according to the settings until stopped
"""
##### Imports
import sys
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

# Own modules
sys.path.append("../../")
sys.path.append("../../drivers/")
import nidaqusb
import lablib.logfile as logfile
import lablib.utils as utils
##### End of imports

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)


aichannel = config.getint('Experiment', 'aichannel')
voltlimit = config.getfloat('Experiment', 'voltlimit')
samplerate = config.getint('Experiment', 'samplerate')

## setup logging
log = logfile.setupLog("voltrecord_long")

# Save configuration info
f = open(configfile)
for line in f:
    log("# %s" %line.strip())
f.close()

# Setup task
dev = nidaqusb.NIDAQ()
task0 = dev.createTask(channel="ai%d" %(aichannel),
                       maxsample=samplerate,
                       rate=samplerate,
                       voltlimit=voltlimit,
                       finite=False,
                       )

# Continuous sampling, let's go!
task0.Start()
from time import time
start = time()
while True:

    try:
        read, data = task0.Read()
        print "Elapsed: "+utils.elapsed(time() - start)
        for val in data:
            log(val)
    except (KeyboardInterrupt):
        break

task0.Stop()

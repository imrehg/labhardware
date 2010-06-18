
from nidaqmx import *
from time import strftime
import logging

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

task = AnalogInputTask()
task.create_voltage_channel('Dev1/ai0', terminal = 'rse', min_val=0, max_val=10.0)
task.configure_timing_sample_clock(rate = 500.0, sample_mode='continuous')

task.start()

while True:
    try:
        data = task.read(2000)
        for d in data:
            logger.info(d[0])
        print "Written!"
    except KeyboardInterrupt:
        del task
        print "Finished"


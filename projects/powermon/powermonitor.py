from time import time, sleep, strftime
import logging
 
import powermeter

# Setup powermeter
meter = powermeter.PowerMeter()

# Setup output file
logger = logging.getLogger()
logfile = "powermon_%s.log" %(strftime("%y%m%d_%H%M%S"))
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 

start = time()
# Logging timestep 
tstep = 0.1

while True:
    try:
        if (time() - start < tstep):
            continue
        now = time()
        fvalue = meter.getReading()
        print "%.3fs -> %e W" %((now-start), fvalue)
        logger.info("%f,%e" %(now, fvalue))
        start = now
    except (KeyboardInterrupt):
        print "Logging finished"
        break

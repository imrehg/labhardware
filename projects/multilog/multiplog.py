import sys
sys.path.append('../../serial')
import serialmulti
import logging
from time import strftime, time

# Setup output file
logger = logging.getLogger()
logfile = "%s.log" %(strftime("%y%m%d_%H%M%S"))
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 

multi = serialmulti.Multimeter()
while True:
    try:
        now = time()
        data = multi.ask()
        print "%g %s" %(data[0], data[1])
        logger.info("%.1f,%g,%s" %(now, data[0], data[1]))
    except KeyboardInterrupt:
        break
multi.close()

import sys
sys.path.append('../../drivers')
import gwmulti
import logging
from time import strftime, time

# Setup output file
logger = logging.getLogger()
logfile = "multi_%s.log" %(strftime("%y%m%d_%H%M%S"))
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 

multi = gwmulti.MultiMeter(4)
while True:
    try:
        now = time()
        data = multi.getnumber()
        if data and data['value']:
            value = data['value']
            unit = data['unit']
            print "%d %g %s" %(now, value, unit)
            logger.info("%.1f,%g,%s" %(now, value, unit))
    except KeyboardInterrupt:
        break
multi.close()

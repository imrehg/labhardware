from time import time, strftime
from numpy import savetxt, array
from agilentmultimeter import AgilentMultimeter

import logging
logger = logging.getLogger('serialmulti')
hdlr = logging.FileHandler("templog_%s.log" %(strftime("%y%m%d_%H%M%S")))
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 

# Config settings
multigpib = 6

# Setting up multimeter Agilent - 34401
multi = AgilentMultimeter(gpib = multigpib)
if (multi == None):
    exit
multi.reset()
# Resistance measurement - 2 Wire
multi.write("CONF:RESISTANCE")
multi.write("RESISTANCE:RESOLUTION MAX")
multi.write("RESISTANCE:NPLC 10")
multi.write("TRIG:SOUR IMM")
# Need to do one reading to set up Wait-For-Trigger state!
multi.ask("READ?")

# Setting up output file
logger.info("#Time(UnixTime) Resistance(Ohm)")

# Do logging until stopped by Ctrl-C
while True:
    try:
        start = time()
        resistance = float(multi.ask("READ?"))
        now = time()
        measuretime = (now + start) / 2
        elapsed = now - start
        result = array([[measuretime, resistance]])
        logger.info("%f %s" % (measuretime, resistance)) 
        print "%f Ohm / %f s" %(resistance, elapsed)
    except (KeyboardInterrupt):
        break

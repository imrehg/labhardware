from time import time, strftime, sleep
from numpy import savetxt, array
from agilentcounter import AgilentCounter

counter = AgilentCounter(gpib=1)
counter.reset()
counter.setupFast()
# Measure frequency on channel 1
counter.write(":FUNC 'FREQ 1'")
counter.setupGating(0.1)

datafile = "beat_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')

while True:
    try:
        start = time()
        counter.initMeasure()
        freq = counter.getFreq()
        now = (time() + start) / 2
        result = array([[now, freq]])
        savetxt(out, result)
        print "%f Hz" %(freq)
    except (KeyboardInterrupt):
        break
out.close()
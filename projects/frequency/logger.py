from time import time, strftime, sleep
from numpy import savetxt, array
from agilentcounter import AgilentCounter
from agilentmultimeter import AgilentMultimeter

# Config settings
countergpib = 1
multigpib = 6
vrange = 1
vresolution = 0.0001

# Setting up frequency counter
counter = AgilentCounter(gpib = countergpib)
counter.reset()
counter.setupFast()
counter.write(":FUNC 'FREQ 1'")
counter.setupGating(0.1)

# Setting up multimeter
multi = AgilentMultimeter(gpib = multigpib)
multi.reset()

# Setting up output file
datafile = "beat_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')
savetxt(out, "Time(UnixTime) BeatFrequency(Hz) Voltage(V)")

while True:
    try:
        start = time()
        counter.initMeasure()
        volts = multi.getDCVoltage(vrange,vresolution)
        freq = counter.getFreq()
        now = (time() + start) / 2
        result = array([[now, freq, volts]])
        savetxt(out, result)
        print "%f Hz / %f V" %(freq, volts)
    except (KeyboardInterrupt):
        break
out.close()

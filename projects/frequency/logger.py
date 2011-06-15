from time import time, strftime
from numpy import savetxt, array
from sys import path

path.append("../../drivers")
from agilentcounter import AgilentCounter
from agilentmultimeter import AgilentMultimeter

# Config settings
countergpib = 5
multigpib = None
vrange = 1
vresolution = 0.0001
gatetime = 0.1 # in seconds

# Setting up frequency counter
counter = AgilentCounter(gpib = countergpib)
if (counter == None):
    exit
counter.reset()
counter.setupFast()
counter.write(":FUNC 'FREQ 1'")
counter.setupGating(gatetime)

# Setting up multimeter
multi = AgilentMultimeter(gpib = multigpib) if multigpib else None

if multi:
    multi.reset()
    # 5-1/2 digits fast
    multi.write("CONF:VOLT:DC %d" %(vrange))
    multi.write("VOLT:DC:NPLC 0.2")
    multi.write("TRIG:SOUR IMM")
    # Need to do one reading to set up Wait-For-Trigger state!
    multi.ask("READ?")

# Setting up output file
datafile = "freqlog_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')
header = ["#Time(UnixTime)"]
if counter:
    header += ["BeatFrequency(Hz)"]
if multi:
    header += ["Voltage(V)"]
header += ["\n"]
out.write(" ".join(header))

# Do logging until stopped by Ctrl-C
while True:
    try:
        start = time()
        counter.initMeasure()
        if multi:
            volts = float(multi.ask("READ?"))
        freq = counter.getFreq()
        now = time()
        if multi:
            measuretime = (now + start) / 2
        else:
            measuretime = start
        elapsed = now - start

        if counter and multi:
            result = array([[measuretime, freq, volts]])
            savetxt(out, result)
            print "%f Hz / %f V / %f s" %(freq, volts, elapsed)
        elif counter:
            result = array([[measuretime, freq]])
            savetxt(out, result)
            print "%f Hz / %f s" %(freq, elapsed)

    except (KeyboardInterrupt):
        break
out.close()

from time import time, strftime, sleep
from numpy import savetxt, array
from agilentcounter import AgilentCounter
import ConfigParser as cp
import sys

try:
    configfile = sys.argv[1]
    config = cp.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    raise
    sys.exit(1)

# Config settings
countergpib = config.getint('Setup','counter_GPIB')
measureconf = config.items('Measurements')

## Convert measurement parameters into numbers
measureconfarray = []
for m in measureconf:
    measureconfarray += [[float(m[0]), int(m[1])]]
measureconfarray.sort()

# Setting up frequency counter
counter = AgilentCounter(gpib = countergpib)
if (counter == None):
    exit
counter.reset()
counter.setupFast()
counter.write(":FUNC 'FREQ 1'")
counter.write(":FREQ:ARM:STAR:SOUR IMM")
counter.write(":FREQ:ARM:STOP:SOUR TIM")

for measure in measureconfarray:
    gatetime = measure[0]
    repeats = measure[1]

    counter.write(":FREQ:ARM:STOP:TIM %f" %(gatetime))
    counter.write(":INIT:CONT ON")
    counter.write(":INIT")

    print "Averaging time: %g" %(gatetime)

    # # Setting up output file
    datafile = "allan_%s_%g.log" %(strftime("%y%m%d_%H%M%S"), gatetime)
    out = file(datafile, 'a')
    out.write("#Time(UnixTime) Frequency(Hz)\n")

    start = time()
    for i in xrange(repeats):

        #### Need such routine to avoid timeout
        ### wait until it is nearly time to ask for the result
        ### but only when the gating time is long
        if (gatetime > 2):
            stoptime = start + gatetime -1
            while time() < stoptime:
                try:
                    sleep(0.1)
                except KeyboardInterrupt:
                    out.close()
                    print "Interrupt by user"
                    sys.exit(1)

        # Ask for the result, this also starts the next measurement
        freq = float(counter.ask("FETCH:FREQ?"))
        finish = time()
        counter.write(":FREQ:EXP1 %s" %freq)
        elapsed = finish - start
        start = finish
        # Print result to file and screen
        result = array([[finish, freq]])
        savetxt(out, result)
        print "%g Hz (elapsed: %.3f s) " %(freq, elapsed)

    out.close()


"""
Keep saving data according to the settings until stopped
"""
##### Imports
from __future__ import division
import sys
import numpy as np
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


pdchannel = config.getint('Experiment', 'pdchannel')
voltlimit = config.getfloat('Experiment', 'voltlimit')
triggerchannel = config.getint('Experiment', 'triggerchannel')
repeats = config.getint('Experiment', 'repeats')

## setup logging
log = logfile.setupLog("pzt")

# Save configuration info
f = open(configfile)
for line in f:
    log("# %s" %line.strip())
f.close()

# Header
log("#"*10)
log("# Frequency(Hz) AmplitudeMean, AmplitudeStd, PhaseMean, PhaseStd")

# Setup task
dev = nidaqusb.NIDAQ()
import fitting

while True:
    try:
        freq = int(raw_input("Frequency (Hz) (hit enter to stop): "))
    except (ValueError):
        break

    timel = 1/freq
    rate = 200000
    sample = int(timel * rate * 2.5)

    dt = 1/rate
    datatime = np.array(map(lambda i: dt*i, range(sample)))

    task0 = dev.createTask(channel="ai%d" %(pdchannel),
                       maxsample=sample,
                       rate=rate,
                       voltlimit=voltlimit,
                       finite=True,
                       )
    task0.SetTrigger("PFI%d" %(triggerchannel))

    amplitudes = np.zeros(repeats)
    phases = np.zeros(repeats)
    for x in range(repeats):
        task0.Start()
        read, data = task0.Read()
        task0.Stop()
        p, vf = fitting.dofit(freq, datatime, data, 2)
        amplitudes[x] = p[0]
        phases[x] = p[1]
        sys.stdout.write("#")
    sys.stdout.write("\n")

    amean, adev = np.mean(amplitudes), np.std(amplitudes)
    pmean, pdev = np.mean(phases), np.std(phases)
    out = "%g, %g, %g, %g, %g" %(freq, amean, adev, pmean, pdev)
    log(out)
    print "Amplitude: %g (%g) " %(amean, adev)
    print "Phases: %g (%g) " %(pmean, pdev)
    print

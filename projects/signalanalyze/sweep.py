import numpy as np
from time import sleep
import matplotlib
matplotlib.rcParams['backend'] = 'wx'
import matplotlib.pylab as pl
from time import time, strftime, sleep
import ConfigParser
import sys
import logging

sys.path.append("../../drivers")
import sr785

# Get config file
try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except IndexError:
    print "No configuration file was given."
    sys.exit(1)
except IOError:
    print "Cannot find configuration file."
    sys.exit(1)

# Load configuraion
GPIB = config.getint('Setup','gpib_num')
start_freq = config.getint('Experiment','start_freq')
stop_freq = config.getint('Experiment','stop_freq')
npoints = config.getint('Experiment','points')
linear_type = config.getboolean('Experiment','linear_type')

# Setup output file
logger = logging.getLogger()
logfile = config.get('Setup','logfile')
if logfile == 'auto':
    logfile = "sweep_%s.log" %(strftime("%y%m%d_%H%M%S"))
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) 
# Save configuration info
f = open(configfile)
for line in f:
    logger.info("# %s" %line.strip())
f.close()
logger.info("#"*10)
logger.info("# Frequency (Hz), LogMagnitude (dB), Phase (deg)")

##### Actual measurement
device = sr785.StanfordSR785(GPIB)

# Turn both displays live
device.write("DISP 0,1")
device.write("DISP 1,1")
device.write("MGRP 2,3")  # Swept Sine measurement group p437
device.write("MEAS 2,47")  # Frequency response p437
device.write("VIEW 0,0")  # Log magnitude, p440
device.write("VIEW 1,5")  # Phase, p440

# Set start and stop frequencies
device.write("SSTR 2,%d" %(start_freq))
device.write("SSTP 2,%d" %(stop_freq))
print "Start frequency:", device.ask("SSTR ? 0")
print "Stop frequency :", device.ask("SSTP ? 0")
device.write("SRPT 2,0")  # single shot experiment, p432
stype = 0 if linear_type else 1
device.write("SSTY 2,%d" %(stype))
device.write("SNPS 2,%d" %(npoints))  # set the number of points swewpt, p433

if linear_type:
    f = np.linspace(start_freq, stop_freq, npoints)
else:  # Logaritmic type
    f = np.logspace(np.log10(start_freq), np.log10(stop_freq), npoints)
f = f.reshape(npoints, 1)  # make column vector

device.ask("DSPS?")  # Clear display messages
device.write("STRT")  # start scan

dataa, datab = False, False
now = time()
try:
    while not dataa or not datab:
        sleep(1)
        res = device.display_status_word(int(device.ask("DSPS ?")))
        codes = res[1]
        if 'SSA' in codes:
            dataa = True
        if 'SSB' in codes:
            datab = True
        print "%.1f seconds..." %(time()-now)
except KeyboardInterrupt:
    sys.exit(0)

# If finished, get and save data
data = device.getdata(2)
out = np.concatenate((f, data),axis=1)
outfile = file(logfile, 'a')
np.savetxt(outfile, out, fmt="%.4e", delimiter=',')
outfile.close()

# Do plotting
pl.subplot(211)
pl.semilogx(f, data[:, 0])
pl.xlabel("Frequency (Hz)")
pl.ylabel("LogMagnitude (dB)")
pl.xlim([f[0], f[-1]])

pl.subplot(212)
pl.semilogx(f, data[:, 1])
pl.xlabel("Frequency (Hz)")
pl.ylabel("Phase (deg)")
pl.xlim([f[0], f[-1]])

pl.show()
    

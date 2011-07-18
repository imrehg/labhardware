"""
Frequency counting with Tektronix RSA3408A Spectrum Analyzer
"""
##### Imports
import sys
import time
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

# Own modules
sys.path.append("../../")
sys.path.append("../../drivers/")
import rsa3408a
import lablib.logfile as logfile
import lablib.utils as utils
##### End of imports

print "Spectrum Analyzer carrier frequency:"
try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Setup instrument
rsagpib = config.getint('Setup', 'rsa_gpib')
rsa = rsa3408a.RSA(rsagpib)

try:
    nums = int(raw_input("How many points (press enter for infinite logging): "))
except:
    nums = None

## setup logging
log = logfile.setupLog("rsa_log")
# Save configuration info
f = open(configfile)
for line in f:
    log("# %s" %line.strip())
f.close()

log("# Unixtime, Carrier_frequency (Hz)")

rsa.write(":INIT:CONT OFF;")
count = 0
for i in xrange(100):
    try:
        cfreq = float(rsa.ask(":READ:SPECtrum:CFR?"))
        now = time.time()
        log("%.3f,%.3f" %(now, cfreq))
        count += 1
        print "Center freq %3d: %.3f Hz" %(count,cfreq)
        if nums and (count >= nums):
            break
    except (KeyboardInterrupt):
        break
print("Finished.")

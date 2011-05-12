import sys
import ConfigParser

# Device drivers
import sma100a
import stanfordSR830

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Initial setup
siggen = sma100a.SMA100A(config.getint('Setup','siggen_GPIB'))
lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))

if not((siggen is None) or (lockin is None)):
    print "Success!"
else:
    print "Fail, check connections or settings"
    

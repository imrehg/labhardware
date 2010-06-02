import sys
import ConfigParser

import agilent8644
import stanfordSR830

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Import configuration and do basic setup
synth = agilent8644.Agilent8644(config.getint('Setup','synth_GPIB'))
lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))

if not((synth is None) or (lockin is None)):
    print "Success!"
else:
    print "Fail, check connections or settings"
    

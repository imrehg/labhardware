import sys
import ConfigParser

import agilentawg
import agilentcounter
import agilentmultimeter

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# Import configuration and do basic setup
funcgen = agilentawg.AgilentAWG(config.getint('Setup','funcgen_GPIB'))
multimeter = agilentmultimeter.AgilentMultimeter(config.getint('Setup','multimeter_GPIB'))
counter = agilentcounter.AgilentCounter(config.getint('Setup','counter_GPIB'))

if not((funcgen is None) or (multimeter is None) or (counter is None)):
    print "Success!"
else:
    print "Fail, check connections or settings"


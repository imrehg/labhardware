from __future__ import division

from time import sleep, strftime
from numpy import *
import ConfigParser
import sys
import logging

# Own modules
sys.path.append("../../drivers")
import agilent81150
import stanfordSR830
import agilent53230

try:
    configfile = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
except:
    print "Cannot find configuration file."
    sys.exit(1)

# def checklock(beatfreq, setfreq):
#     """ Panic switch if unlocked laser is detected """
#     # if abs(abs(setfreq) - beatfreq) > 1000:
#     #     print "Unlocked!"
#     #     sys.exit(1)
#     pass

def experiment():
    # Import configuration and do basic setup
    funcgen = agilent81150.Agilent81150(config.getint('Setup','funcgen_GPIB'))
    lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))
    counter = agilent53230.Counter(config.getint('Setup','counter_GPIB'))

    # Get settings from config file
    aomcentre = config.getfloat('Experiment','aomcentre')
    aomscan = [config.getfloat('Experiment','scanstart'),
               config.getfloat('Experiment','scanstop')]
    aomscansteps = config.getint('Experiment','scansteps')
    repeats = config.getint('Experiment','repeats')
    amchannel = config.getint('Experiment','amchannel')
    amdepth = config.getint('Experiment', 'amdepth')
    amfrequency = config.getfloat('Experiment','amfrequency')
    # Check Manual for the meaning of these integers: pages 5-13 and 5-6
    lockinsensitivity = config.getint('Experiment','lockinsensitivity')
    lockinrate = config.getint('Experiment','lockinrate')
    lockintimeconstant = config.getint('Experiment','lockintimeconstant')
    startdelay = config.getfloat('Experiment','startdelay')
    lockinch1 = config.getfloat('Experiment','lockinch1')
    lockinch2 = config.getfloat('Experiment','lockinch2')
    # Counter
    counterchannel = config.getint('Experiment', 'counterchannel')
    
    # Setup logging
    logger = logging.getLogger()
    logfile = config.get('Setup','logfile')
    if logfile == 'auto':
        logfile = "pressureshift_%s.log" %(strftime("%y%m%d_%H%M%S"))
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

    # Setup instruments
    # Function generator
    funcgen.write(":FREQ%d %f" %(amchannel, aomcentre))
    print("Set Channel %d amplitude manually!" %(amchannel))
    # funcgen.write(":VOLTAGE%d:AMPLITUDE %fmVpp" %(amchannel, aomamp)) # do not set anymore!
    funcgen.write(":AM%d:DEPTH %dPCT" %(amchannel, amdepth))
    funcgen.write(":AM%d:INT:FREQUENCY %f" %(amchannel, amfrequency))
    funcgen.write(":AM%d:STATE On" %(amchannel))
    # Lock-in amplifier
    lockin.write("REST")
    lockin.write("SRAT %d" %(lockinrate))
    lockin.write("OFLT %d" %(lockintimeconstant))
    lockin.write("SENS %d" %(lockinsensitivity))
    lockin.write("DDEF1,%d,0" %(lockinch1))
    lockin.write("DDEF2,%d,0" %(lockinch2))
    lockin.write("TSTR 1") # Trigger start scan

    q = ["SRAT?", "SPTS?", "SEND?", "OFLT?", "SENS?"]
    for quest in q:
        print quest, "->", lockin.ask(quest)
    # Make the gatetime equal to the lockin amp's sample rate implied gatetime
    samplerate = lockin.getSampleRate()
    gatetime = 1/samplerate["value"]
    print("Samplerate %g Hz (%gs gatetime)" %(samplerate["value"], gatetime))
    ## Counter setup
    counter.setupFreqBatch(channel=counterchannel, count=repeats, gatetime=gatetime)

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
    logging.info("#AOMFrequency(Hz) MeasuredBeat(Hz) LockInSignal(V)")
    ss = linspace(aomscan[0],aomscan[1],aomscansteps)
    for index, scanning in enumerate(ss):
        #### Steps
        ## Adjust AOM frequency
        print "Detuning %d / %d: %f Hz" %(index+1, aomscansteps, scanning) 
        
        # Set and read back function generator frequency for scanning
        funcgen.write(":FREQ%d %f" %(amchannel, aomcentre+scanning))
        setfreq = float(funcgen.ask(":FREQ%d?" %(amchannel))) - aomcentre
        lockin.write("REST")
        counter.write("INIT")
        sleep(startdelay)

        # Start!
        lockin.write("TRIG")
        counter.write("*TRG")

        # Wait until all done!
        while (int(lockin.ask("SPTS?")) < repeats):
            sleep(0.2)

        ## Get data from Locking then beat frequency
        tempch1 = lockin.ask("TRCA?1,0,%d" %(repeats))
        tempoutch1 = array([float(x) for x in tempch1.split(',') if not (x == '')])
        tempch2 = lockin.ask("TRCA?2,0,%d" %(repeats))
        tempoutch2 = array([float(x) for x in tempch2.split(',') if not (x == '')])

        ## "R?" and "DATA:REM?" has different format!
        beatfreq = array([float(x) for x in counter.ask("DATA:REM? %d,WAIT" %(repeats)).split(',')])

        ## Write out data
        for index in xrange(repeats):
            logger.info("%.4f,%e,%e,%.4f" %(setfreq, tempoutch1[index], tempoutch2[index], beatfreq[index]))


def connectiontest():
    """ Check if connection can be established with the given settings """
    funcgen = agilent81150.Agilent81150(config.getint('Setup','funcgen_GPIB'))
    lockin = stanfordSR830.StanfordSR830(config.getint('Setup','lockin_GPIB'))
    counter = agilent53230.Counter(config.getint('Setup','counter_GPIB'))

    if None not in [funcgen, lockin, counter]:
        print "Success!"
    else:
        print "Fail, check connections or settings"

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[2] == "connection":
        connectiontest()
    else:
        experiment()

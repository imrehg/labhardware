"""
Uploading triggerable data to the spatial light modulator

TODO:
+ How to treat the two masks?
+ Error handling
+ Generalization: make it importable or use import from other slmcontrol?
+ Confirmation before upload
+ Show in file-selection title the index of the file to be uploaded ("select file #3")
+ Store settings in conf
+ Automatic port selection
"""

#!/usr/bin/env python
import sys

import ConfigParser
import os
import numpy as np

#import cri_slm_fake as cri_slm
import cri_slm
import ourgui

if __name__ == "__main__":
    slm = cri_slm.SLM()

    try:
        config = ConfigParser.RawConfigParser()
        config.read(dirname+'/slm.conf')
    except:
        print "Error when parsing/applying settings. Continue anyway."
        pass

    inputFiles = []
    while True:
        filename = ourgui.openFile()
        if filename == "":
            break
        else:
            inputFiles += [filename]

    ninput = len(inputFiles)
    print("Selected %d files" %(ninput))
    if ninput == 0:
        sys.exit(1)

    # Load data files
    data = np.zeros((128, ninput))
    for i in xrange(ninput):
        temp = np.loadtxt(inputFiles[i])
        data[:,i] = temp

    # Upload data frame-by-frame
    print "Upload data..."
    slm.cmdmask("0");
    for i in xrange(128):
        slm.cmdframe("%d" %i);
        slm.blockset(data[:, i % ninput].tolist())

    ## Clear the other mask
    print "Clear other mask..."
    slm.cmdmask("1");
    for i in xrange(128):
        slm.cmdframe("%d" %i);
        slm.clearframe();
    slm.cmdframe("0");

    ## Go back to the beginning
    slm.cmdmask("0");
    slm.cmdframe("0");

    print "Done"

"""
Transfering data from Stanford Research SR785 Signal analyzer
"""
import numpy as np
import sys

# Own modules
sys.path.append("../../")
sys.path.append("../../drivers/")
import sr785

GPIB = 2
try:
    device = sr785.StanfordSR785(GPIB)
except (IOError):
    print("Couldn't find things on GPIB channel %d, exiting" %(GPIB))
    sys.exit(1)

print device.ask("*IDN?")

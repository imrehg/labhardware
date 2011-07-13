"""
Utility functions
"""
from __future__ import division

def elapsed(sec):
    """
    Formatting elapsed time display
    """
    mins, rem = int(sec / 60), sec % 60
    text = "%.1f" %(rem)
    ending = "s"
    if mins > 0:
        text = "%d:" %(mins) + text
        ending = "m"
    return text+ending

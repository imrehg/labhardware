"""
Commong logging routines in the measurement software
"""
import logging
from time import strftime

class LogFile:
    """
    Setup logging to file with automatically generated timestamp name
    """

    def __init__(self, basename=None):
        if not basename:
            basename = ""
        else:
            basename += "_"
        self.logfile = "%s%s.log" %(basename, strftime("%y%m%d_%H%M%S"))

        hdlr = logging.FileHandler(self.logfile)
        formatter = logging.Formatter('%(message)s')
        hdlr.setFormatter(formatter)

        self.logger = logging.getLogger()
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO) 
        
    def log(self, message):
        self.logger.info(message)

def setupLog(basename=None):
    """
    Return a logging function to a new logfile
    """
    logfile = LogFile(basename)
    return logfile.log

#!/usr/bin/env python
import sys

#import matplotlib 
#matplotlib.use('GTK') 
#from matplotlib.figure import Figure 
#from matplotlib.axes import Subplot 
#from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar 
#from matplotlib.numerix import arange, sin, pi 

import ConfigParser
import os

try: 
    import pygtk 
    pygtk.require("2.0") 
except: 
    pass 
try: 
    import gtk
    import gtk.gdk
    import gobject
    import gtk.glade 
except: 
    sys.exit(1)

import cri_slm_fake as cri_slm

 
class appGui: 
    def __init__(self, slm):
        self.slm = slm
        self.moveenabled = False
        dirname = os.path.dirname(sys.argv[0])
        gladefile = dirname + "/simple.glade"
        self.windowname = "window1" 
        self.wTree = gtk.glade.XML(gladefile, self.windowname)
        dic = {"on_mainWindow_destroy" : gtk.main_quit}
        self.wTree.signal_autoconnect(dic)
        self.window = self.wTree.get_widget(self.windowname)
        self.window.show_all()
        dic = {"on_window1_destroy" : gtk.main_quit, 
              }
        self.wTree.signal_autoconnect(dic)
        self.masklabel = self.wTree.get_widget("MaskLabel")
        self.masklabeltext = self.masklabel.get_label()
        self.framelabel = self.wTree.get_widget("FrameLabel")
        self.framelabeltext = self.framelabel.get_label()
        self.elementlabel = self.wTree.get_widget("ElementLabel")
        self.elementlabeltext = self.elementlabel.get_label()
        self.valuelabel = self.wTree.get_widget("ValueLabel")
        self.valuelabeltext = self.valuelabel.get_label()

        self.updatelabels()

#         self.poslabel = self.wTree.get_widget("PositionLabel")
        self.window.connect('key-press-event', self.windowkey)

    def updatelabels(self):
        """ Get info and update labels """
        self.masklabel.set_markup(self.masklabeltext+" %d"%self.slm.cmdmask("?"))
        self.framelabel.set_markup(self.framelabeltext+" %d"%self.slm.cmdframe("?"))
        self.elementlabel.set_markup(self.elementlabeltext+" %d"%self.slm.cmdelement("?"))
        self.valuelabel.set_markup(self.valuelabeltext+" %d"%self.slm.cmdvalue("?"))
        return

    def windowkey(self, widget, event):
        """ What to do when a key is pressed? """
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        if name == 'm':
            self.togglemask()
        elif name == 'f':
            self.changetarget(1, self.slm.cmdframe, self.slm.maxframe)
            self.slm.activeframe(self.slm.cmdframe("?"))
        elif name == 'd':
            self.changetarget(-1, self.slm.cmdframe, self.slm.maxframe)
            self.slm.activeframe(self.slm.cmdframe("?"))
        elif name == 'e':
            self.changetarget(1, self.slm.cmdelement, self.slm.maxelement)
        elif name == 'w':
            self.changetarget(-1, self.slm.cmdelement, self.slm.maxelement)
        elif name == 'Right':
            self.changetarget(1, self.slm.cmdvalue, self.slm.maxvalue)
        elif name == 'Left':
            self.changetarget(-1, self.slm.cmdvalue, self.slm.maxvalue)
        elif name == 'Page_Up':
            self.changetarget(100, self.slm.cmdvalue, self.slm.maxvalue)
        elif name == 'Page_Down':
            self.changetarget(-100, self.slm.cmdvalue, self.slm.maxvalue)
        elif name == 'c':
            self.clearframe()

    def togglemask(self):
        """ Toggle between the two masks (not portable!) """
        self.slm.cmdmask(1-self.slm.cmdmask("?"))
        self.updatelabels()

    def changetarget(self, change, command, maxcommand):
        """ Change mask/frame/element/drive level """
        currentvalue = command("?")
        newvalue = currentvalue + change
        if newvalue < 0:
            newvalue = maxcommand()-1
        elif newvalue >= maxcommand():
            newvalue = 0
        command(newvalue)
        self.updatelabels()

    def clearframe(self):
        """ Clear current frame """
        self.slm.clearframe()
        self.updatelabels()


if __name__ == "__main__":
    dirname = os.path.dirname(sys.argv[0])
    slm = cri_slm.SLM('/dev/ttyUSB0')

    try:
        config = ConfigParser.RawConfigParser()
        config.read(dirname+'/slm.conf')
    except:
        print "Error when parsing/applying settings. Continue anyway."
        pass
    app = appGui(slm)
    gtk.main()

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

import transstage

def catch_button(window, event, label):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        print event.state
        mod = gtk.accelerator_get_label(keyval,event.state)
        label.set_markup('<span size="xx-large">%s\n%d</span>'% (mod, keyval))
 
 
class appGui: 
    def __init__(self, cont):
        self.cont = cont
        self.moveenabled = False
        dirname = os.path.dirname(sys.argv[0])
        gladefile = dirname + "/experiment02.glade"
        self.windowname = "window1" 
        self.wTree = gtk.glade.XML(gladefile, self.windowname)
        dic = {"on_mainWindow_destroy" : gtk.main_quit}
        self.wTree.signal_autoconnect(dic)
        self.window = self.wTree.get_widget(self.windowname)
        self.window.show_all()
        dic = {"on_window1_destroy" : gtk.main_quit, 
              }
        self.wTree.signal_autoconnect(dic)
        self.poslabel = self.wTree.get_widget("PositionLabel")
        self.window.connect('key-press-event', self.windowkey)

        self.stepbuttons = []
        for i in range(5):
            self.stepbuttons.append(self.wTree.get_widget("stepbutton%d"%(i+1)))
        self.stepbuttons[0].set_active(True)
        self.stepscale = self.wTree.get_widget("StepScalePull")

        # Step sizes of 1um, 1mm, 10mm
        self.stepsizes = [10000, 1000, 100, 10, 1]
        # From measurement
        self.scale = 6487485 / 200000.0 * 1.875

        self.pollposition(self.poslabel)
        gobject.timeout_add(1000, self.pollposition, self.poslabel)
        self.moveenabled = True

        # Set move direction
        self.moveposbtn = self.wTree.get_widget("MovePosBtn")

        # Alternative position
        self.altpos = None

        self.homesetbtn = self.wTree.get_widget("button1")
        self.homesetbtn.connect('clicked', self.homeset)
        self.gohomebtn = self.wTree.get_widget("button2")
        self.gohomebtn.connect('clicked', self.gohome)

        self.setaltposbtn = self.wTree.get_widget("SetAltPosBtn")
        self.setaltposbtn.connect('clicked', self.setaltpos)
        self.goaltposbtn = self.wTree.get_widget("GoToAltPosBtn")
        self.goaltposbtn.connect('clicked', self.goaltpos)
        self.altposlabel = self.wTree.get_widget("AltPosLabel")
        self.altposlabel.set_text("Not set")

        self.scandirbtn = self.wTree.get_widget("ScanDirButton")
        self.scandirbtn.connect('clicked', self.scandirchange)
        self.scanstartstopbtn = self.wTree.get_widget("ScanStartStopBtn")
        self.scanstartstopbtn.connect('clicked', self.scanstartstop)
        self.scanning = None
        self.currentstep = None
        self.scantimes = [2000, 1000, 500, 100]
        self.scantimechoice = []
        for i in range(4):
            self.scantimechoice.append(self.wTree.get_widget("ScanTime%d"%(i)))
        self.scantimechoice[0].set_active(True)

    def countfum(self, um):
        return int(self.scale * um)

    def umfcount(self, count):
        return count / self.scale
        
    def windowkey(self, widget, event):
        direction = ["-", '+']
        if not self.moveposbtn.get_active():
            direction.reverse()
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        if (name == "Left"):
            self.movestage(direction[0])
        elif (name == "Right"):
            self.movestage(direction[1])
        elif (name == "Page_Up"):
            self.stepmultiplier(True)
        elif (name == "Page_Down"):
            self.stepmultiplier(False)

    def stepmultiplier(self, increase):
        i, m = self.getstepparams()
        if (increase):
            if (i == 0) and (m == 9):
                return
            m = m + 1
        else:
            if (i == (len(self.stepsizes)-1)) and (m == 1):
                return
            m = m - 1
        if (m > 9):
            m = 1
            i = i - 1
        elif (m < 1):
            m = 9
            i = i + 1
        self.stepbuttons[i].set_active(True)
        self.stepscale.set_value(m)

    def getstepsize(self):
        i, multiplier = self.getstepparams()
        return self.countfum(self.stepsizes[i]*multiplier)

    def getstepparams(self):
        i = 0
        for button in self.stepbuttons:
            if not button.get_active():
                i = i + 1
            else:
                break
        multiplier = self.stepscale.get_value()
        return (i, multiplier)

    def movestage(self, direction, distance=None):
        if distance == None:
            distance = self.getstepsize()
        if (direction == "-"):
            distance *= -1
        if self.moveenabled :
            cont.command("MR%d"%(distance), 0)

    def pollposition(self, label):
        pos = self.cont.getposition()
        label.set_text("%d count\n%.4f mm"%(pos, \
                       self.umfcount(pos)/1000))
        return True

    def homeset(self, widget):
        # Refresh the alternative position
        current = self.cont.getposition()
        self.setaltpos(self, position=(self.altpos - current))
        # Set home
        cont.command("DH")

    def gohome(self, widget):
        cont.command("MA0")

    def setaltpos(self, widget=None, position=None):
        if not position:
            self.altpos = self.cont.getposition()
        else:
            self.altpos = position
        self.altposlabel.set_text("%.4f mm" \
                                  %(self.umfcount(self.altpos)/1000.0))

    def goaltpos(self, widget):
        if self.altpos:
            self.cont.command("MA%d" %(self.altpos))

    def getscantime(self):
        i = 0
        for choice in self.scantimechoice:
            if not choice.get_active():
                i = i + 1
            else:
                break
        return self.scantimes[i]

    def scandirchange(self, widget):
        # Not Active: Home, Active: alternative
        widget.set_label("%s" \
                        %(("Scan to Home", "Scan to Alternative")[widget.get_active()]))

    def scanstartstop(self, widget):
        if widget.get_active():
            self.startscan()
        else:
            self.stopscan()

    def startscan(self):
        self.scandirbtn.set_sensitive(False)
        self.scanstartstopbtn.set_active(True)
        self.scanstartstopbtn.set_label("Stop")
        if self.scandirbtn.get_active():
            target = self.altpos
        else:
            target = 0
        scanpause = self.getscantime()
        self.scanning = gobject.timeout_add(scanpause, self.scanstep, target)

    def stopscan(self):
        try:
            gobject.source_remove(self.scanning)
        except:
            pass
        finally:
            self.scanning = None
        self.scandirbtn.set_sensitive(True)
        self.scanstartstopbtn.set_active(False)
        self.scanstartstopbtn.set_label("Start")

    def scanstep(self, target):
        # If there's no target, don't scan
        if target == None:
            self.stopscan()
            return False
        if not ("Trajectory complete" in self.cont.getstatus()):
            return True
        aimstep = self.getstepsize()
        pos  = self.cont.getposition()
        diff = (target - pos)
        # If within threshold, stop scanning
        if abs(diff) < 30:
            self.stopscan()
            return False
        stepsize = abs(diff) if (abs(diff) < aimstep) else aimstep
        newpos = pos + int(diff * (diff/ abs(diff)))
        self.currentstep = newpos
        if (diff == abs(diff)):
            direction = '+'
        else:
            direction = '-'
        self.movestage(direction, stepsize)
        return True

if __name__ == "__main__":
    dirname = os.path.dirname(sys.argv[0])
    cont = transstage.MotorControl('/dev/ttyUSB0')

    splash = gtk.Window()
    splashimg = gtk.Image()
    splashimg.set_from_file(dirname+'/splash.svg')
    splash.add(splashimg)
    splash.show_all()
    # Needed to display splash during the setup sequence
    while gtk.events_pending():
        gtk.main_iteration()
    try:
        config = ConfigParser.RawConfigParser()
        config.read(dirname+'/stage.conf')
        section = 'PID'
        for opt in config.options(section):
            print "Set %s -> %s" %(opt, config.get(section, opt))
            cont.setparam(opt, int(config.get(section, opt)))
    except:
        print "Error when parsing/applying settings. Continue anyway."
        pass
    splash.hide()
    app = appGui(cont)
    gtk.main()

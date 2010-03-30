#!/usr/bin/env python
import sys

#import matplotlib 
#matplotlib.use('GTK') 
#from matplotlib.figure import Figure 
#from matplotlib.axes import Subplot 
#from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar 
#from matplotlib.numerix import arange, sin, pi 

import ConfigParser

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
        gladefile = "experiment02.glade" 
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

        # Step sizes of 1um, 1mm, 10mm
        self.stepsizes = [10000, 1000, 100, 10, 1]
        # From measurement
        self.scale = 6487485 / 200000.0 * 1.875

        self.pollposition(self.poslabel)
        gobject.timeout_add(1000, self.pollposition, self.poslabel)
        self.moveenabled = True

        self.homesetbtn = self.wTree.get_widget("button1")
        self.homesetbtn.connect('clicked', self.homeset)
        self.gohomebtn = self.wTree.get_widget("button2")
        self.gohomebtn.connect('clicked', self.gohome)

    def countfum(self, um):
        return int(self.scale * um)

    def umfcount(self, count):
        return count / self.scale
        
    def windowkey(self, widget, event):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        if (name == "Left"):
            self.movestage("-")
        elif (name == "Right"):
            self.movestage("+")

    def movestage(self, direction):
        i = 0
        for button in self.stepbuttons:
            if not button.get_active():
                i = i + 1
            else:
                break
        distance = self.countfum(self.stepsizes[i])
        if (direction == "-"):
            distance *= -1
        if self.moveenabled :
            cont.command("MR%d"%(distance))

    def pollposition(self, label):
        pos = self.cont.getposition()
        label.set_text("%d count\n%.4f mm"%(pos, \
                       self.umfcount(pos)/1000))
        return True

    def homeset(self, widget):
        cont.command("DH")

    def gohome(self, widget):
        cont.command("MA0")

if __name__ == "__main__":
    cont = transstage.MotorControl('/dev/ttyUSB0')
    try:
        config = ConfigParser.RawConfigParser()
        config.read('stage.conf')
        section = 'PID'
        for opt in config.options(section):
            print "Set %d -> %s" %(opt, config.get(section, opt))
            cont.setparam(opt, int(config.get(section, opt)))
    except:
        pass
    app = appGui(cont)
    gtk.main()

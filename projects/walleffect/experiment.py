#!/usr/bin/env python
import sys

#import matplotlib 
#matplotlib.use('GTK') 
#from matplotlib.figure import Figure 
#from matplotlib.axes import Subplot 
#from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar 
#from matplotlib.numerix import arange, sin, pi 

try: 
    import pygtk 
    pygtk.require("2.0") 
except: 
    pass 
try: 
    import gtk
    import gtk.gdk
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
        self.label1 = self.wTree.get_widget("label1")
        self.window.connect('key-press-event', self.windowkey, self.label1)

        self.stepbtn1 = self.wTree.get_widget("radiobutton1")
        self.stepbtn2 = self.wTree.get_widget("radiobutton2")
        self.stepbtn3 = self.wTree.get_widget("radiobutton3")

        self.stepbtns = [self.stepbtn1, self.stepbtn2, self.stepbtn3]
        self.stepbtn3.set_active(True)
        # Step sizes of 1um, 1mm, 10mm
        self.stepsizes = [1, 1000, 10000]
        # From measurement
        self.scale = 6487485 / 200000.0 * 1.875

    def countfum(self, um):
        return int(self.scale * um)

    def umfcount(self, count):
        return count / self.scale
        
    def windowkey(self, widget, event, label):
        self.movestage("+")

    def movestage(self, direction):
        for i in range(len(self.stepbtns)):
            if (self.stepbtns[i].get_active()):
                stepsize = i
                break
        


if __name__ == "__main__":
    
    cont = transstage.MotorControl('/dev/ttyUSB0')
    app = appGui(cont)
    gtk.main()

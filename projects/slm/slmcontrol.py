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
    import pango
except:
    sys.exit(1)

#import cri_slm_fake as cri_slm
import cri_slm
 
class appGui:
    def __init__(self, slm):
        self.slm = slm
        self._saved = None
        self.moveenabled = False
        dirname = os.path.dirname(sys.argv[0])
        if len(dirname) >  0:
            dirname += "/"
        gladefile = dirname + "simple.glade"
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

        fontdesc = "Sans 36"
        self.masklabel.modify_font(pango.FontDescription(fontdesc))
        self.framelabel.modify_font(pango.FontDescription(fontdesc))
        self.elementlabel.modify_font(pango.FontDescription(fontdesc))
        self.valuelabel.modify_font(pango.FontDescription(fontdesc))

        self.updatelabels()

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
        elif name == 'o':
            self.wholeframechange(-10)
        elif name == 'O':
            self.wholeframechange(-1)
        elif name == 'p':
            self.wholeframechange(10)
        elif name == 'P':
            self.wholeframechange(1)
        elif name == 's':
            self.savevalues()
        elif name == 'l':
            self.loadvalues()
        elif name == 'S':
            self.savetofile()
        elif name == 'L':
            self.loadfromfile()
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

    def wholeframechange(self, change):
        """ Move the whole frame value together up or down """
        try:
            change = int(change)
        except:
            return
        values = self.slm.blockquery()
        def limit(u):
            if u < 0:
                return 0
            elif u > 4095:
                return 4095
            else:
                return u
        update = [limit(v + change) for v in values]
        self.slm.blockset(update)
        self.updatelabels()

    def savevalues(self):
        self._saved = self.slm.blockquery()

    def loadvalues(self):
        if not (self._saved is None):
            self.slm.blockset(self._saved)
        self.updatelabels()

    def savetofile(self):
        saveframe = gtk.FileChooserDialog(title="Save current frame", parent=None,
                                          action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                          buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                                          backend=None)
        saveframe.set_default_response(gtk.RESPONSE_OK)
        response = saveframe.run()
        if response == gtk.RESPONSE_OK:
            name = saveframe.get_filename()
            inframe = open(name, 'w')
            values = self.slm.blockquery()
            for v in values:
                inframe.write("%d\n" %v)
        saveframe.destroy()

    def loadfromfile(self):
        loadframe = gtk.FileChooserDialog(title="Load into current frame", parent=None,
                                          action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                          buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_OPEN, gtk.RESPONSE_OK),
                                          backend=None)
        loadframe.set_default_response(gtk.RESPONSE_OK)
        response = loadframe.run()
        if response == gtk.RESPONSE_OK:
            name = loadframe.get_filename()
            try:
                inframe = open(name, 'r')
                values = []
                for line in inframe.readlines():
                    values.append(int(line))
                self.slm.blockset(values)
                self.updatelabels()
            except:
                pass
        loadframe.destroy()


if __name__ == "__main__":
    dirname = os.path.dirname(sys.argv[0])
    slm = cri_slm.SLM()

    try:
        config = ConfigParser.RawConfigParser()
        config.read(dirname+'/slm.conf')
    except:
        print "Error when parsing/applying settings. Continue anyway."
        pass
    app = appGui(slm)
    gtk.main()

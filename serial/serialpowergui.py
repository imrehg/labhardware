#!/usr/bin/env python

# Very simple Gui for reading values from Newport  Optical Power Meter 1830-C
# Display, plus interaction
#
# TODO:
# Command queuing
# Rate control
# More setting buttons to control all available things (Light, Attenuation, ...)
# Logging
# Rolling graph of values
# Check cross-platform behaviour

import serial
import wx

ser = serial.Serial('/dev/ttyUSB0',baudrate=9600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=2, xonxoff=1)

def sendCom(command):
    ser.write("%s\n" % (command))

def readReply():
    return(ser.readline().strip())

def getUnit():
    sendCom("U?")
    unit = readReply();
    unitHuman = {
        '1': lambda : "W",
        '2': lambda : "dB",
        '3': lambda : "dBm",
        '4': lambda : "rel"
    }[unit]()
    return(unitHuman)

def getReading():
    sendCom("D?")
    value = readReply();
    return(value)

def getLight():
    sendCom("K?")
    light = readReply();
    return(int(light))

def setLight(light):
    if (light in [0,1,2]):
        sendCom("K%d" % (light))

ID_LIGHTBTN = 100
class MainPanel(wx.Panel):
    def __init__(self, parent, log, frame=None):
        wx.Panel.__init__(
            self, parent, -1,
            style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN|wx.NO_FULL_REPAINT_ON_RESIZE
            )
        self.frame = frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        dataSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.reading = wx.TextCtrl(self, -1, "N/A",style=wx.TE_READONLY)
        dataSizer.Add(self.reading, 0, wx.EXPAND|wx.ALL, 2)
        self.unit = wx.TextCtrl(self, -1, "N/A",style=wx.TE_READONLY)
        dataSizer.Add(self.unit, 0, wx.CENTER|wx.ALL, 2)
        #~ self.unit = wx.TextCtrl(self, -1, "N/A",wx.Point(100, 30),size=wx.Size(30,30),style=wx.TE_READONLY)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        lightBtn = wx.Button(self, ID_LIGHTBTN, "Light")
        btnSizer.Add(lightBtn, 1, wx.EXPAND)
        wx.EVT_BUTTON(self, ID_LIGHTBTN, self.on_light_clk)


        sizer.Add(dataSizer, 0, wx.EXPAND)
        sizer.Add(btnSizer, 0, wx.EXPAND)
        self.SetSizer(sizer)


        self.unit.SetValue(getUnit())
        self.reading.SetValue(getReading())

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnClose)

        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer = wx.Timer(self,-1)
        self.timer.Start(1000/15)

    def OnClose(self,evt):
        print "Closing"
        ser.close()
        self.timer.Stop()
        self.timer = None

    def OnTimer(self, evt):
        self.reading.SetValue(getReading())

    def on_light_clk(self, evt):
        light = getLight() + 1
        if (light > 2) :
            light = 0
        setLight(light)

class wkFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Optical Power Meter", size=wx.Size(200,200))
        self.panel = MainPanel(self, -1)
        #~ self.CreateStatusBar()

class wkApp(wx.App):
    def OnInit(self):
        self.mainFrame = wkFrame()
        self.mainFrame.Show()

        return True

app = wkApp(redirect=False)
app.MainLoop()

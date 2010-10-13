#!/usr/bin/env python
from __future__ import division
import sys, time, os, gc

import matplotlib
import matplotlib.pyplot as plt
import numpy as npy

import ctypes as C
import pylab
import numpy
import scipy
import time
import png

def imgSnap(session, width, height):
	image = numpy.ndarray(shape=(height, width), dtype=C.c_uint8)
	bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))

	#imgSnap (Sid, (void **)&ImaqBuffer); //NI-IMAQ function
	err = imaq.imgSnap(sid, C.byref(bufAddr))
	if (err < 0):
		text = C.c_char_p('')
		imaq.imgShowError(err, text)
		print "SnapError: %s" %(text.value)
	return image
	
def imgGrab(session, width, height):
    image = numpy.ndarray(shape=(height, width), dtype=C.c_uint8)
    bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))

    #imgSnap (Sid, (void **)&ImaqBuffer); //NI-IMAQ function
    err = imaq.imgGrab(sid, C.byref(bufAddr), 1)
    if (err < 0):
        text = C.c_char_p('')
        imaq.imgShowError(err, text)
        print "GrabError: %s" %(text.value)
    return image

if __name__ == '__main__':
    imaq = C.windll.imaq
    INTERFACE_ID = C.c_uint32
    SESSION_ID = C.c_uint32
    iid = INTERFACE_ID(0)
    sid = SESSION_ID(0)
    index = C.c_uint32(0)
    name = C.c_char_p('')
    imaq.imgInterfaceQueryNames(index, name)
    print "ifaceopen: ", imaq.imgInterfaceOpen(name, C.byref(iid))
    print "sessionopen: ", imaq.imgSessionOpen(iid, C.byref(sid)); 

    # USER_FUNC imgGetAttribute(uInt32 void_id, uInt32 attribute, void* value);
    _IMG_BASE = 0x3FF60000
    IMG_ATTR_ROI_WIDTH = _IMG_BASE + 0x01A6
    IMG_ATTR_ROI_HEIGHT = _IMG_BASE + 0x01A7
    width, height = C.c_uint32(), C.c_uint32()
    print "imageattr: ", imaq.imgGetAttribute(sid, IMG_ATTR_ROI_WIDTH, C.byref(width))
    print "imageattr: ", imaq.imgGetAttribute(sid, IMG_ATTR_ROI_HEIGHT, C.byref(height))
    print "Image size: %d x %d "%(width.value, height.value)
    print imaq.imgSessionStopAcquisition(sid)
    print "Grab: ", imaq.imgGrabSetup(sid, 1)

    # grabbed =  imgGrab(0, width.value, height.value)
    print '>' * 60
    image_num = int(raw_input("Image sequence number:"))
    nrep = int(raw_input("Number of repetitions:"))
    notes = raw_input("Notes:")
    for i in range(nrep):
    	time.sleep(0.3)
    	grabbed =  imgGrab(0, width.value, height.value)
	filename = "grab_%04d_%02d.png" %(image_num,i)
    	# plt.imsave("grab_%04d_%0i.png" %(image_num,i), grabbed, format="PNG", cmap=gray)

	grabline = numpy.reshape(grabbed, (-1, width.value*height.value))
	pngfile = open(filename, 'wb') 
	pngWriter = png.Writer(width.value, height.value,
                           greyscale=True,
                           alpha=False,
                           bitdepth=8)
	pngWriter.write(pngfile, grabbed)
	pngfile.close()
    infofile = open("grab_%04d_info.txt" %(image_num), 'w')
    infofile.write("Repeats: %d\n" %nrep)
    infofile.write(notes)
    infofile.close()

    void_id = C.c_uint32(0)
    freeresources = C.c_uint32(0)
    imaq.imgSessionStopAcquisition(sid)
    imaq.imgClose(sid, True)
    imaq.imgClose(iid, True)
    print "Finished"

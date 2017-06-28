# -*- coding: utf-8 -*-
"""
From PyqtGraph examples.

Raspberry Pi cam monitor via http.

"""

## Add path to library (just for examples; you do not need this)
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import urllib, cStringIO
from PIL import Image

# Set http path to the Raspberry Pi you have
URL='http://192.168.1.130/html/cam.jpg'
interval=30 # Time interval to request image from Raspberry pi in millisecond.
app = QtGui.QApplication([])

## Create window with GraphicsView widget
win = pg.GraphicsLayoutWidget()
win.show()  ## show widget alone in its own window
win.setWindowTitle('Rydberg laser lock monitor')
view = win.addViewBox()

## lock the aspect ratio so pixels are always square
#view.setAspectLocked(True)

## Create image item
img = pg.ImageItem()
view.addItem(img)

# Read image once and save the proper image dimension.
file = cStringIO.StringIO(urllib.urlopen(URL).read())
data = np.array(Image.open(file))
dims_correct= np.shape(data)

def updateData():
    #global img, data, updateTime, fps
    file = cStringIO.StringIO(urllib.urlopen(URL).read())
    data = np.array(Image.open(file))
    dims_current=np.shape(data)

    # Sometimes data can be correct so let's check if we got non-corrupted file.
    if (dims_correct==dims_current):
        data=np.flip(data.transpose(1,0,2),1)
        ## Display the data
        img.setImage(data)
    QtCore.QTimer.singleShot(interval, updateData)

updateData()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
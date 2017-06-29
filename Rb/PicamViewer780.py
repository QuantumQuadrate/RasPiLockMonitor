# -*- coding: utf-8 -*-
"""
From PyqtGraph examples.

Raspberry Pi cam monitor via http.

Last update : 2017-06-28
Author : Minho Kwon
"""

## Add path to library (just for examples; you do not need this)
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import urllib2, cStringIO
from PIL import Image
import time
import collections

#pg.setConfigOptions(useOpenGL=True)
# Set http path to the Raspberry Pi you have
URL='http://128.104.162.15:10000/html/cam.jpg'
interval=30 # Initial time interval to request image from Raspberry pi in millisecond. Interval will be automatically adjusted.
app = QtGui.QApplication([])

# Read an image to display in case nothing to show.
noimagefile=np.array(Image.open('noimage.png'))
timeout=0.5 # in seconds
latencies=collections.deque(maxlen=20)
percentile=90
threshold=50

## Create window with GraphicsView widget
win = pg.GraphicsLayoutWidget()
win.show()  ## show widget alone in its own window
win.setWindowTitle('Pi Camera Viewer by Minho')
view = win.addViewBox()
view.setAspectLocked(True) # lock the aspect ratio so pixels are always square

ModeSelect=0 # 0: Laser lock monitor, 1: High Power laser safety , 2: General monitoring

## Create image item and textitem
img = pg.ImageItem()
text= pg.TextItem()
text2= pg.TextItem()
view.addItem(img)
view.addItem(text)
view.addItem(text2)
text.setAnchor((0,2))
text2.setAnchor((-1,7))

# Read image once and save the proper image dimension.

try:
    text.setText("Connecting to {}".format(URL))
    file = cStringIO.StringIO(urllib2.urlopen(URL,timeout=timeout).read())
    data = np.array(Image.open(file))
    dims_correct = np.shape(data)
except IOError:
    text.setText("Attempting to {} but timed out after {} sec".format(URL, timeout))
    img.setImage(np.flip(noimagefile.transpose(1, 0, 2), 1))


def updateData(latencies=latencies,interval=interval,timeout=timeout,mode=ModeSelect,percentile=percentile):
    try:
        starttime=time.time()
        file = cStringIO.StringIO(urllib2.urlopen(URL,timeout=timeout).read())
        data = np.array(Image.open(file))
        dims_current = np.shape(data)
        latestlatency=int(1000 * (time.time() - starttime))
        latencies.append(latestlatency)  # record response time and use it to dynamically adapt the network instability.
        interval = min(1000, max(35, np.mean(latencies) + 4 * np.std(latencies)))
        if (dims_correct == dims_current):
            data = np.flip(data.transpose(1, 0, 2), 1) # numpy flip requires >v1.13.0
            img.setImage(data)
            text.setHtml("<font size=4>From {} <br /> "
                         "Latency: {} ms, refresh time : {} ms <br/>"
                         "Mean brightness:{}, {}th percentile:{} <br/>"
                         "threshold:{}".format(URL, int(latestlatency), int(interval), int(np.mean(data)),
                                                     int(percentile), int(np.percentile(data, percentile)),threshold))
            if (mode == 0):  # 0: Laser lock monitor,
                if (int(np.percentile(data, percentile)) > threshold):
                    text2.setHtml("<font size=10>LOCKED")
                else:
                    text2.setHtml("<font size=10>UNLOCKED")
            elif (mode == 1):  # 1: High Power laser safety
                if (int(np.percentile(data, percentile)) > threshold):
                    text2.setHtml("<font size=10>HIGH POWER LASER IN USE <br/>"
                                  "WEAR SAFETY GOGGLES")
                else:
                    text2.setHtml("<font size=10>Safe to enter")
        else:
            text.setHtml("Image corrupted")

    except IOError:
        img.setImage(np.flip(noimagefile.transpose(1,0,2),1))
        text.setText("Attempting to {} but timed out after {} sec".format(URL,timeout))

    QtCore.QTimer.singleShot(interval, updateData)

updateData()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

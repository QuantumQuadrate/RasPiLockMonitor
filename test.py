## Add path to library (just for examples; you do not need this)
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import urllib, cStringIO
from PIL import Image

# Set http path to the Raspberry Pi you have
URL='http://192.168.1.130/html/cam.jpg'
interval=30 # Time interval to request image from Raspberry pi in millisecond.

## Create window with GraphicsView widget

## lock the aspect ratio so pixels are always square
#view.setAspectLocked(True)

## Create image item


# Read image once and save the proper image dimension.
try:
    file = cStringIO.StringIO(urllib.urlopen(URL).read())
except IOError:
    print "IO Error!!"
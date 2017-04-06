# Server program
from PIL import Image, ImageStat
import socket
import time

HOST = ''
PORT = 50007

def open_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    return s

def open_connection(s):
    conn, addr = s.accept()
    s.settimeout(None)
    return conn

def get_avg_brightness():
    im = Image.open('/dev/shm/mjpeg/cam.jpg').convert('L')
    stat = ImageStat.Stat(im)
    total = stat.mean[0]
    return total

print "Opening Connection..."
s = open_listener()
while 1:
    print "Waiting..."
    conn = open_connection(s)
    data = conn.recv(1024)
    if data == 'Brightness':
        brightness = get_avg_brightness()
        conn.sendall(str(brightness))
        print "Prompted brightness, returned %f" % brightness
    else:
        conn.setblocking(False)
        threshold = float(data)
        print "Experiment started, monitoring lock (Threshold %f)" % threshold
        isFinished = False
        frame_threshold = 10
        dropped_frames = 0
        while not isFinished:
            if get_avg_brightness() < threshold:
                if dropped_frames < frame_threshold:
                    dropped_frames += 1
                else:
                    print "Lock broke at %s" % time.strftime("%H:%M:%S")
                    try:
                        conn.sendall('Lock broken')
                    except Exception as e:
                        print "Socket died. {}".format(e)
                        isFinished = True
                        break
                    conn.setblocking(True)
                    f = conn.recv(1024)
                    conn.setblocking(False)
                    print "Experiment Resumed"
            else:
                dropped_frames = 0
            try:
                f = conn.recv(1024)
                if f is not None:
                    isFinished = True
            except Exception as e:
                pass
                
        print "Experiment Finished"
    conn.close()

#!/usr/bin/env python

import random
import sys
import os.path
import threading
import socket
import sys
from PIL import Image

HOST = '151.217.47.77'
PORT = 8080

def pixel(sock, x, y, r, g, b, a=255):
    if a == 255:
        sock.send('PX %d %d %02x%02x%02x\n' % (x, y, r, g, b))
    else:
        sock.send('PX %d %d %02x%02x%02x%02x\n' % (x, y, r, g, b, a))


def worm(x, y, n, r, g, b):
    while n:
        pixel(x, y, r, g, b, 25)
        x += random.randint(0, 2) - 1
        y += random.randint(0, 2) - 1
        n -= 1


def writeImage(offsetX, offsetY, im):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    _, _, w, h = im.getbbox()
    for x in xrange(w):
        for y in xrange(h):
            r, g, b = im.getpixel((x, y))
            pixel(sock, x + offsetX, y + offsetY, r, g, b)


def writePixelFlutImage(threadName, im):
    print(threadName)
    while True:
        writeImage(random.randint(0, 924), random.randint(0, 924), im)


def launchThreaded(numberOfThreads):
    threads = []
    #try:
    for x in range(0, numberOfThreads):
        #thread.start_new_thread(writePixelFlutImage, ("Launched thread " + str(x), im,))
        t = threading.Thread(target=writePixelFlutImage, args=("Launched thread #" + str(x), im))
        threads.append(t)
        t.start()
    #except:
     #   print("Error: unable to start thread")

def printUsage():
    print('Usage: pixelflut <PATH-TO-PNG-FILE-TO-SEND> <NUMBER-OF-THREADS>')
    print('       <PATH-TO-PNG-FILE-TO-SEND>:   full path to the image file to be sent')
    print('       <NUMBER-OF-THREADS>:          number of threads to send images in parallel')

if len(sys.argv) < 2:
    printUsage()
    sys.exit()

inputFileName = sys.argv[1]
if inputFileName == '':
    printUsage()
    sys.exit()

print('Sending ' + inputFileName + ' via ' + sys.argv[2] + ' threads')

im = Image.open(inputFileName).convert('RGB')
im.thumbnail((100, 100), Image.ANTIALIAS)
launchThreaded(int(sys.argv[2]))




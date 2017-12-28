#!/usr/bin/env python

import random
import sys
import os.path
import threading
import socket
import sys
import yaml
from PIL import Image

config = []
with open("config.yml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

HOST = config['host']
PORT = config['port']

def pixel(sock, x, y, r, g, b, a=255):
    if a == 255:
        sock.send('PX %d %d %02x%02x%02x\n' % (x, y, r, g, b))
    else:
        sock.send('PX %d %d %02x%02x%02x%02x\n' % (x, y, r, g, b, a))

def getSize(sock):
    sock.send('SIZE\n')
    data = sock.recv(1024)
    rawData = data.replace('\n', '').split(' ')
    rawData.remove('SIZE')
    return rawData

def worm(x, y, n, r, g, b):
    while n:
        pixel(x, y, r, g, b, 25)
        x += random.randint(0, 2) - 1
        y += random.randint(0, 2) - 1
        n -= 1

def getNewSocket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

def writeImage(offsetX, offsetY, im):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    _, _, w, h = im.getbbox()
    for x in xrange(w):
        for y in xrange(h):
            r, g, b = im.getpixel((x, y))
            pixel(sock, x + offsetX, y + offsetY, r, g, b)


def writePixelFlutImage(threadName, im, serverScreenSize):
    print(threadName)
    _, _, w, h = im.getbbox()
    while True:
        writeImage(random.randint(0, int(serverScreenSize[0]) - w), random.randint(0, int(serverScreenSize[1]) - h), im)


def launchThreaded(numberOfThreads, serverScreenSize):
    threads = []
    try:
        for x in range(0, numberOfThreads):
            t = threading.Thread(target=writePixelFlutImage, args=("Launched thread #" + str(x), im, serverScreenSize))
            threads.append(t)
            t.start()
    except:
        print("Error: unable to start thread")

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

numberOfThreads = int(sys.argv[2])

print('Sending ' + inputFileName + ' via ' + sys.argv[2] + ' threads')

sizeSock = getNewSocket(config['host'], config['port'])
size = getSize(sizeSock)
sizeSock.close()

im = Image.open(inputFileName).convert('RGB')
im.thumbnail((config['imageWidth'], config['imageHeight']), Image.ANTIALIAS)
launchThreaded(numberOfThreads, size)




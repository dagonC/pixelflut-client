#!/usr/bin/env python

import random
import sys
import os.path
import threading
import socket
import sys
import yaml
from PIL import Image


def pixel(sock, x, y, r, g, b, a=255):
    if a == 255:
        sock.send('PX %d %d %02x%02x%02x\n' % (x, y, r, g, b))
    else:
        sock.send('PX %d %d %02x%02x%02x%02x\n' % (x, y, r, g, b, a))

def getSize(config):
    sock = getNewSocket(config['host'], config['port'])
    sock.send('SIZE\n')
    data = sock.recv(1024)
    sock.close()
    rawData = data.replace('\n', '').split(' ')
    rawData.remove('SIZE')
    return rawData

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
            if TRANSPARENCY:
                if r != TRANSPARENT_R or g != TRANSPARENT_G or b != TRANSPARENT_B:
                    pixel(sock, x + offsetX, y + offsetY, r, g, b)
            else:
                pixel(sock, x + offsetX, y + offsetY, r, g, b)
    sock.close()


def writePixelFlutImage(threadName, im, serverScreenSize):
    print(threadName)
    _, _, w, h = im.getbbox()
    while True:
        writeImage(random.randint(0, int(serverScreenSize[0]) - w), random.randint(0, int(serverScreenSize[1]) - h), im)

def writePixelFlutImageTile(threadName, im, x, y):
    print(threadName + ' x.y = ' + str(x) + '.' + str(y))
    _, _, w, h = im.getbbox()
    while True:
        writeImage(x, y, im)

def launchThreaded(numberOfThreads, serverScreenSize):
    threads = []
    try:
        for threadCount in range(0, numberOfThreads):
            t = threading.Thread(target=writePixelFlutImage, args=("Launched thread #" + str(threadCount), im, serverScreenSize))
            threads.append(t)
            t.start()
    except:
        print("Error: unable to start thread")

def printUsage():
    print('Usage: pixelflut <pos-x> <pos-y>')

def crop(im,height,width):
    imgwidth, imgheight = im.size
    for i in range(imgheight//height):
        for j in range(imgwidth//width):
            box = (j*width, i*height, (j+1)*width, (i+1)*height)
            yield im.crop(box)

def getImageTiles(im, tileWidth, tileHeight):
    tiles = []
    start_num = 0
    for k, piece in enumerate(crop(im, tileHeight, tileWidth), start_num):
        imageTile = Image.new('RGB', (tileHeight, tileWidth), 255)
        imageTile.paste(piece)
        tiles.append(imageTile)
    return tiles

def launchTiled(tiles, imageWidth, imageHeight, tileWidth, tileHeight, serverScreenSize):
    threads = []
    x = 0
    y = 0
    baseOffsetX = DRAW_OFFSET_X
    baseOffsetY = DRAW_OFFSET_Y
    for tileCount in range(0, len(tiles)):
        imageTile = tiles[tileCount]
        if (tileWidth + x) > imageWidth:
            y = (tileHeight + y)
            x = 0
        x = (tileWidth + x)
        t = threading.Thread(target=writePixelFlutImageTile,
                             args=("Launched thread for tile #" + str(tileCount), imageTile, x + baseOffsetX, y + baseOffsetY))
        threads.append(t)
        t.start()

if len(sys.argv) != 3:
    printUsage()
    sys.exit()

config = []
with open("config.yml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

HOST = config['host']
PORT = config['port']
DRAW_OFFSET_X = int(sys.argv[1])
DRAW_OFFSET_Y = int(sys.argv[2])

tranparencyConfig = config['transparency']
TRANSPARENCY = bool(tranparencyConfig['enabled'])
TRANSPARENT_R = int(tranparencyConfig['transparentR'])
TRANSPARENT_G = int(tranparencyConfig['transparentG'])
TRANSPARENT_B = int(tranparencyConfig['transparentB'])

print('Sending ' + config['file'] + ' to ...')
print(' host:             ' + config['host'] + ':' + str(config['port']))
serverScreenSize = getSize(config)
print(' host screen size: ' + serverScreenSize[0] + 'x' + serverScreenSize[1])

im = Image.open(config['file']).convert('RGB')
im.thumbnail((config['imageWidth'], config['imageHeight']), Image.ANTIALIAS)

tileWidth=config['tileWidth']
tileHeight=config['tileHeight']
tiles = getImageTiles(im, tileWidth, tileHeight)
print('using ' + (str(len(tiles))) + ' tiles (' + str(config['tileWidth']) + 'x' + str(config['tileHeight']) + ')')

launchTiled(tiles, config['imageWidth'], config['imageHeight'], tileWidth, tileHeight, serverScreenSize)





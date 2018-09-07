# -*- coding: utf-8 -*-
"""
Created on  Jun 16 22:39:34 2016

@author: AnkitSingh
"""

from Imagehandler import Imagehandler
import yaml
import glob
import os
import cv2 as cv
#from pyzbar.pyzbar import decode


ADDRESS = 'Input/qr5.jpg'

def App():
    #载入yaml文件，以文件名作为输入
    with open('config.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    IOPlaces = cfg['Main']
    input = IOPlaces['Input']
    output = IOPlaces['Output']
    directorypath = input
    os.chdir(input)
    filesTypes = cfg['FileType']
    images = []
    for filetype in filesTypes:
        images.extend(glob.glob('*.' + filetype))
    paths = [directorypath + image for image in images]
    
    #处理函数
    for i in xrange(len(paths)):
        obj = Imagehandler(paths[i])
        TransformImage = obj.QRCodeInImage()
        if TransformImage is None:
            print ('Image is not generated')
        obj.WritingImage(
            TransformImage, str(output), 'output' + str(i) + '.jpg')

def main():
    img = cv.imread(ADDRESS, cv.IMREAD_COLOR)
    if img is None:
        print ('no img')
    else:
        print (img.shape)
    obj = Imagehandler(img)
    TransformImage = obj.QRCodeInImage()
    if TransformImage is None:
        print ('Image is not generated')
    obj.WritingImage(
        TransformImage, 'QRimage')
    #result = decode(TransformImage)
    #print (result[0].data)
if __name__ == '__main__':
    main()

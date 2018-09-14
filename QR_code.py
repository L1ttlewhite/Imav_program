#!/usr/bin/env python
# coding: u8
import os
import zbar
from PIL import Image 
import cv2
import numpy as np

#cap = cv2.VideoCapture(0)
# create a reader
scanner = zbar.ImageScanner()

# configure the reader
scanner.parse_config('enable')
frame =  cv2.imread('left.jpg',0)
while(1):
    #ret, frame = cap.read()
    cv2.imshow("img0", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    pil = Image.fromarray(frame).convert('L')
    width, height = pil.size
    #pil.show()
    raw = pil.tobytes()

    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    scanner.scan(image)

    tmpdata=''
    # extract results
    for symbol in image:
        # do something useful with results
        print symbol.type, '图片内容为:\n%s' % symbol.data
        tmpdata=tmpdata+symbol.data

# clean up
del(image)
cap.release()
cv2.destroyAllWindows() 

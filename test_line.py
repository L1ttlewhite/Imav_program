import time
import yaml,os
import rospy 
import cv2 as cv
import numpy as np 
from Camera import Camera
from Line import Linehandler

thre = 100

current_path = os.path.abspath(os.path.dirname(__file__))
'''
img = cv.imread(current_path + '/data/' + '3.jpg')
print img.shape
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
cv.imshow('img',gray)
cv.waitKey(0)
'''
path = current_path + '/data/' + '3.jpg'

Line = Linehandler(mode = 2,  video_num = 0, video_topic = '', image_path = path)
Line.Show_image_color()
Line.Process_image_Thre(thre = thre)

Line.Find_blobs()
Line.Draw_blobs()
line = Line.Find_line()
print line
img = Line.Get_image_color()
cv.line(img, (line[0][1],line[0][0]), (line[-1][1],line[-1][0]), (0,255,0), 10)
cv.imshow('img_ini',img)
cv.waitKey(0)
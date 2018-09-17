import time
import yaml,os
import rospy 
import cv2 as cv
import numpy as np 
from Camera import Camera
from Line import Linehandler

thre = 60

current_path = os.path.abspath(os.path.dirname(__file__))
'''
img = cv.imread(current_path + '/data/' + '3.jpg')
print img.shape
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
cv.imshow('img',gray)
cv.waitKey(0)
'''
path_video = current_path + '/data/' + 'test_video_1.avi'
path_image = current_path + '/data/' + 'test_pic_1.png'
Line = Linehandler(mode = 3,  video_num = 0, video_topic = '', image_path = path_video)

while True:
    Line.Cap_image()
    start = time.time()
    Line.Process_image_Thre(thre = thre)
    Line.Show_image_thre()
    Line.Find_blobs()
    line = Line.Find_line()
    #print line 
    img = Line.Get_image_color().copy()
    Line.Draw_blobs()
    if line:
        cv.line(img, (line[0][1],line[0][0]), (line[-1][1],line[-1][0]), (0,0,255), 10)
    cv.imshow('img', img)
    end   = time.time()
    print end - start
    #cv.waitKey(0)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


    
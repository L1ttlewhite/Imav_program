# -*- coding: UTF-8 -*-

import numpy as np 
import cv2 as cv
import math,time
import yaml,os
import rospy
from Camera import Camera


current_path = os.path.abspath(os.path.dirname(__file__))
with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
    camera_yaml = yaml.load(f.read())
    camera_fx   = camera_yaml['camera_fx']
    camera_fy   = camera_yaml['camera_fy'] 
    camera_bf   = camera_yaml['camera_bf']
    camera_topic =camera_yaml['camera_topic']
    camera_topic_left = camera_yaml['camera_topic_left']
    camera_topic_right = camera_yaml['camera_topic_right']

rospy.init_node('image_handler', anonymous = True)

loop_bottom = np.array([77,69,142])
loop_top = np.array([121,255,255])

Loop_L = Camera(mode = 1, video_num = 0, video_topic = camera_topic_left)    
Loop_R = Camera(mode = 1, video_num = 0, video_topic = camera_topic_right)
while True:
    if Loop_L.isOpen() and Loop_R.isOpen():
        stereo = cv.StereoBM_create(numDisparities=48, blockSize=15)
        Loop_L.Process_image_Thre(thre = 100)
        Loop_R.Process_image_Thre(thre = 100) 
        #Loop_L.Show_image_gray('left')
        #Loop_R.Show_image_gray('right')
        #cv.imshow('left',Loop_L.image_gray)
        
        disparity = stereo.compute(Loop_L.image_gray,Loop_R.image_gray)
        out = cv.threshold(disparity,50,255,cv.THRESH_BINARY)
        print disparity.shape 
        print disparity
        
        cv.imshow('disparity', out)
       
        cv.waitKey(0)
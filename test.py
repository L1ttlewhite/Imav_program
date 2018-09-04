# -*- coding: UTF-8 -*-

import numpy as np 
import time 
import cv2 as cv
import yaml,os
import rospy
from Camera import Camera
from Window import Windowhandler

def filter(x_new, x_old):
    a = 0.8
    return ( x_new * a + (1 - a) * x_old )

x_old, y_old, z_old = 0,0,0
x_new, y_new, z_new = 0,0,0

def stereo_center(x1, y1, x2, y2, fx, fy, bf):   
    x,y,z = 0,0,0
    if abs(x1-x2) <= 40 and abs(x1 - x2) >0:
        z = fx * bf / (x1 - x2)
        x = x1 * z / fx
        y = y1 * z / fy
    return int(x) , int(y), int(z) 


current_path = os.path.abspath(os.path.dirname(__file__))
with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
    camera_yaml = yaml.load(f.read())
    camera_fx   = camera_yaml['camera_fx']
    camera_fy   = camera_yaml['camera_fy'] 
    camera_bf   = camera_yaml['camera_bf']
    camera_topic =camera_yaml['camera_topic']
    camera_topic_left = camera_yaml['camera_topic_left']
    camera_topic_right = camera_yaml['camera_topic_right']




window_bottom = np.array([22,104,0])
window_top = np.array([50,255,255])
rospy.init_node('image_handler', anonymous = True)
#window_L = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_left)    
#window_R = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_right)
window = Windowhandler(mode=0, video_num=0)
while not rospy.is_shutdown():
    window.Cap_image()
    if window.isOpen():
        window.Process_image(HSV_low = window_bottom, HSV_high = window_top)
        window.Get_contours()
        window.WindowFinding()
        #window.Find_center()
        #window.Show_image_thre()
        #window.Show_contours()
        window.Show_contours_window()
        cv.waitKey(1)
    # if window_L.isOpen() and window_R.isOpen():
    #     start = time.time()
    #     window_L.Process_image(HSV_low = window_bottom,HSV_high = window_top)
    #     window_R.Process_image(HSV_low = window_bottom,HSV_high = window_top)
    #     window_L.Get_contours()
    #     window_R.Get_contours()
    #     window_L.Find_center()
    #     window_R.Find_center()
    #     #window.Show_contours()
    #     window_L.Show_contours_window('image_left')
    #     window_R.Show_contours_window('image_right')
    #     if window_L.isFind() and window_R.isFind():
    #         x1,y1 = window_L.Get_centerid()
    #         x2,y2 = window_R.Get_centerid()
    #         x,y,z = stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bf)
    #         print x1,y1
            
    #     end = time.time()
    #     #print end - start
    #     cv.waitKey(1)
    else:
        print ('No image load')
rospy.spin()  
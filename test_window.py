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
    if x1 and y1 and x2 and y2:
        print abs(x1-x2)
        if abs(x1-x2) <= 50: 
            z = fx * bf / (x1 - x2)
            x = x1 * z / fx
            y = y1 * z / fy
    return x, y, z 


current_path = os.path.abspath(os.path.dirname(__file__))
with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
    camera_yaml = yaml.load(f.read())
    camera_fx   = camera_yaml['camera_fx']
    camera_fy   = camera_yaml['camera_fy'] 
    camera_bf   = camera_yaml['camera_bf']
    camera_topic =camera_yaml['camera_topic']
    camera_topic_left = camera_yaml['camera_topic_left']
    camera_topic_right = camera_yaml['camera_topic_right']

#定义numpy数组来统计各个点的方差
array_x1 = np.zeros(500)
array_y1 = np.zeros(500)
array_x2 = np.zeros(500)
array_y2 = np.zeros(500)
array_x1_x2 = np.zeros(500)
array_x  = np.zeros(500)
array_y  = np.zeros(500)
array_z  = np.zeros(500)
array_count = 0




window_bottom = np.array([6,47,0])
window_top = np.array([56,255,255])
rospy.init_node('image_handler', anonymous = True)
window_L = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_left)    
window_R = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_right)
#window = Windowhandler(mode=0, video_num=1)
while not rospy.is_shutdown():
    # window.Cap_image()
    # if window.isOpen():
    #     window.Process_image(HSV_low = window_bottom, HSV_high = window_top)
    #     window.Get_contours()
    #     window.WindowFinding()
    #     window.Show_contours_window()
    #     cv.waitKey(1)
    if window_L.isOpen() and window_R.isOpen():
        start = time.time()
        window_L.Process_image(HSV_low = window_bottom,HSV_high = window_top)
        window_R.Process_image(HSV_low = window_bottom,HSV_high = window_top)
        window_L.Get_contours()
        window_R.Get_contours()
        window_L.WindowFinding()
        window_R.WindowFinding()
        #window.Show_contours()
        window_L.Show_contours_window('image_left')
        window_R.Show_contours_window('image_right')
        if window_L.isFind() and window_R.isFind():
            x1,y1 = window_L.Get_centerid()
            x2,y2 = window_R.Get_centerid()
            x,y,z = stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bf)
            if x and y and z:
                array_x1[array_count] = x1
                array_y1[array_count] = y1
                array_x2[array_count] = x2
                array_y2[array_count] = y2
                array_x1_x2[array_count] = abs(x1-x2)
                array_x[array_count] = x
                array_y[array_count] = y
                array_z[array_count] = z
                array_count = array_count + 1
            if array_count == 500:
                print ("mean and var of x1 is : {}, {}".format(array_x1.mean(), array_x1.var()))
                print ("mean and var of y1 is : {}, {}".format(array_y1.mean(), array_y1.var()))
                print ("mean and var of x2 is : {}, {}".format(array_x2.mean(), array_x2.var()))
                print ("mean and var of y2 is : {}, {}".format(array_y2.mean(), array_y2.var()))
                print ("mean and var of x1-x2 is : {}, {}".format(array_x1_x2.mean(), array_x1_x2.var()))
                print ("mean and var of x is : {}, {}".format(array_x.mean(), array_x.var()))
                print ("mean and var of y is : {}, {}".format(array_y.mean(), array_y.var()))
                print ("mean and var of z is : {}, {}".format(array_z.mean(), array_z.var()))
                cv.waitKey(0)
            print x1,y1,x2,y2
            print x,y,z
            #cv.waitKey(0) 
        end = time.time()
        #print end - start
        cv.waitKey(1)
    else:
        print ('No image load')
rospy.spin()  
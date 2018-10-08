# -*- coding: UTF-8 -*-

import numpy as np 
import time 
import cv2 as cv
import yaml,os
import rospy
from Camera import Camera
from Window import Windowhandler
from geometry_msgs.msg import Point



def stereo_center(x1, y1, x2, y2, fx, fy, bf):   
    x,y,z = 0,0,0
    if x1 or y1 or x2 or y2:
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



point_pub = rospy.Publisher('uav_position', Point, queue_size=1)
point = Point()
window_bottom = np.array([22,40,0])
window_top = np.array([66,255,255])
rospy.init_node('image_handler', anonymous = True)
window_L = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_left)    
window_R = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_right)
#window = Windowhandler(mode=0, video_num=1)
while not rospy.is_shutdown():
    # window.Cap_image()
    # if window.isOpen():
    #     window.Process_image_HSV(HSV_low = window_bottom, HSV_high = window_top)
    #     window.Get_contours()
    #     window.WindowFinding()
    #     window.Show_contours_window()
    #     x1,y1 = window.Get_centerid()
    #     print x1,y1
    #     cv.waitKey(1)
    if window_L.isOpen() and window_R.isOpen():
        start = time.time()
        window_L.Process_image_HSV(HSV_low = window_bottom,HSV_high = window_top)
        window_R.Process_image_HSV(HSV_low = window_bottom,HSV_high = window_top)
        window_L.Get_contours()
        window_R.Get_contours()
        window_L.WindowFinding()
        window_R.WindowFinding()
        window_L.Show_image_thre('image_left_thre')
        window_R.Show_image_thre('image_right_thre')
        #window_L.Show_contours()
        window_L.Show_contours_window('image_left')
        window_R.Show_contours_window('image_right')
        if window_L.isFind() and window_R.isFind():
            x1,y1 = window_L.Get_centerid()
            x2,y2 = window_R.Get_centerid()
            x1 = x1-160
            y1 = y1-120
            x2 = x2-160
            y2 = y2-120
            x,y,z = stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bf)
            x = x -30
            y = y - 350
            point.x = z
            point.y = x
            point.z = y
            point_pub.publish(point)
            print -x,y,z
            #print ('the center of two window is : {}, {}, {}, {}',format(x1,y1,x2,y2))
            #print ('the 3D point is : {}, {}, {}'.format(-x,y,z))
            #cv.waitKey(0) 
        end = time.time()
        #print end - start
        cv.waitKey(1)
    else:
        print ('No image load')
rospy.spin()  
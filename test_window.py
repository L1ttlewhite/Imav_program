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
        #print abs(x1-x2)
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

#定义numpy数组来拟合最后的点
#array_x  = np.zeros(20)
#array_y  = np.zeros(20)
#array_z  = np.zeros(20)
#array_count = 0


def callback_position(Point):
    global state_position_x, state_position_y, state_position_z
    state_position_x = Point.x
    state_position_y = Point.y
    state_position_z = Point.z


point_pub = rospy.Publisher('uav_position', Point, queue_size=1)
window_pub = rospy.Publisher('window_position', Point, queue_size=1)
point = Point()
point_f = Point()
point_f.x = 0
point_f.y = 0
point_f.z = 0
point_window = Point()

#HSV阈值
window_bottom = np.array([9,49,130])
window_top = np.array([45,130,255])

rospy.init_node('image_handler', anonymous = True)
window_L = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_left)    
window_R = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_right)
rospy.Subscriber("state_position",Point,callback_position)



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
    global state_position_x, state_position_y, state_position_z
    if window_L.isOpen() and window_R.isOpen():
        start = time.time()
        window_L.Process_image_HSV(HSV_low = window_bottom,HSV_high = window_top)
        window_R.Process_image_HSV(HSV_low = window_bottom,HSV_high = window_top)
        window_L.Get_contours()
        window_R.Get_contours()
        window_L.WindowFinding()
        window_R.WindowFinding()
        #window_L.Show_image_thre('image_left_thre')
        #window_R.Show_image_thre('image_right_thre')
        #window_L.Show_contours()
        window_L.Show_contours_window('image_left')
        #window_R.Show_contours_window('image_right')
        if window_L.isFind() and window_R.isFind():
            x1,y1 = window_L.Get_centerid()
            x2,y2 = window_R.Get_centerid()
            x1 = x1-320
            y1 = y1-240
            x2 = x2-320
            y2 = y2-240
            x,y,z = stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bf)
            point_window.x = x
            point_window.y = y
            point_window.z = z
        

            point.x = z/1000 + state_position_x  + 0.5
            point.y = -x/1000 + state_position_y + 0.13 
            point.z = -y/1000 + state_position_z 

            #filter
            point_f.x = 0.7*point_f.x + 0.3*point.x 
            point_f.y = 0.7*point_f.y + 0.3*point.y 
            point_f.z = 0.7*point_f.z + 0.3*point.z
            

            point_pub.publish(point_f)
            window_pub.publish(point_window)
            print point_f.x, point_f.y, point_f.z
            
        end = time.time()
        #print end - start
        cv.waitKey(1)
    else:
        print ('No image load')
rospy.spin()  
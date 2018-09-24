# -*- coding: UTF-8 -*-
import time
import yaml,os
import rospy 
import cv2 as cv
from geometry_msgs.msg import Point

def nothing(x):
    pass

x,y,z = 0,0,0
x_,y_,z_ = 0,0,0

cv.namedWindow('position_param', cv.WINDOW_NORMAL)

cv.createTrackbar('x', 'position_param', 0, 10, nothing)
cv.createTrackbar('y', 'position_param', 0, 10, nothing)
cv.createTrackbar('z', 'position_param', 0, 10, nothing)
cv.createTrackbar('x_', 'position_param', 0, 10, nothing)
cv.createTrackbar('y_', 'position_param', 0, 10, nothing)
cv.createTrackbar('z_', 'position_param', 0, 10, nothing)

point = Point()
pub = rospy.Publisher('uav_position', Point, queue_size = 1)
rospy.init_node('position', anonymous=True)
rate = rospy.Rate(5)

while not rospy.is_shutdown():
    x = float(cv.getTrackbarPos('x','position_param'))
    y = float(cv.getTrackbarPos('y','position_param'))
    z = float(cv.getTrackbarPos('z','position_param'))
    
    x_ = float(cv.getTrackbarPos('x_','position_param'))
    y_ = float(cv.getTrackbarPos('y_','position_param'))
    z_ = float(cv.getTrackbarPos('z_','position_param'))
    
    point.x = x - x_
    point.y = y - y_
    point.z = z - z_
    try:
        pub.publish(point)
    except rospy.ROSInterruptException:
        pass
    cv.waitKey(1)
    rate.sleep()
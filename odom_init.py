# -*- coding: UTF-8 -*-

import numpy as np 
import rospy
import math
import time
import  os    
import  sys  
import  tty, termios  
from numpy.linalg import inv
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Point

init_flag_new = 0 
init_flag_old = 0 

T_CO  = np.zeros((4,4))
T_WO = np.eye(4)


def callback_tf(tf):
    global flag
    global T_WO
    global twist_pub,position_pub
    positon  = Point()
    twist = Point()
    T_CW  = np.zeros((4,4))
    position_x = -tf.transforms[0].transform.translation.x  
    position_y = -tf.transforms[0].transform.translation.y  
    position_z = -tf.transforms[0].transform.translation.z  
    qx = tf.transforms[0].transform.rotation.x
    qy = tf.transforms[0].transform.rotation.y
    qz = tf.transforms[0].transform.rotation.z
    qw = tf.transforms[0].transform.rotation.w
 

    T_CW[0,0] = 1 - 2*qy*qy - 2*qz*qz
    T_CW[0,1] = 2*(qx*qy - qz*qw)
    T_CW[0,2] = 2*(qx*qz + qy*qw)
    T_CW[0,3] = position_x
    T_CW[1,0] = 2*(qx*qy + qz*qw)
    T_CW[1,1] = 1 - 2*qx*qx - 2*qz*qz
    T_CW[1,2] = 2*(qy*qz -qx*qw)
    T_CW[1,3] = position_y
    T_CW[2,0] = 2*(qx*qz - qy*qw)
    T_CW[2,1] = 2*(qy*qz + qx*qw)
    T_CW[2,2] = 1 - 2*qx*qx - 2*qy*qy
    T_CW[2,3] = position_z
    T_CW[3,3] = 1

    if init_flag_old == 0 and init_flag_new ==1 :
        T_WO = inv(T_CW)    
    
    
    T_CO = np.dot(T_CW , T_WO)
    

    roll = math.atan2(T_CO[2,1],T_CO[2,2])
    pitch = math.atan2(-T_CO[2,0], math.sqrt(T_CO[2,1]*T_CO[2,1]+T_CO[2,2]*T_CO[2,2]))
    yaw = math.atan2(T_CO[1,0],T_CO[0,0])
    position_x = T_CO[0,3]
    position_y = T_CO[1,3]
    position_z = T_CO[2,3] 
    positon.x = position_x
    positon.y = position_y
    positon.z = position_z
    position_pub.publish (positon)
    twist.x = roll
    twist.y = pitch
    twist.z = yaw
    twist_pub.publish(twist)


rospy.init_node('udp_image', anonymous = True)
rospy.Subscriber("tf", TFMessage, callback_tf)
position_pub = rospy.Publisher('position',Point,queue_size=1)
twist_pub = rospy.Publisher('twist', Point,queue_size=1)
rate = rospy.Rate(10)
print 'Init is done. Waiting for Key'

while not rospy.is_shutdown():
    fd=sys.stdin.fileno()  
    old_settings=termios.tcgetattr(fd)  
    #old_settings[3]= old_settings[3] & ~termios.ICANON & ~termios.ECHO    
    try:  
        tty.setraw(fd)  
        ch=sys.stdin.read(1)  
    finally:  
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)    
        #print 'error'  
    if ch=='i':
        flag = True
        print 'init odom'  
    elif ord(ch)==0x3:  
        #这个是ctrl c  
        print "shutdown"  
        break  
    rate.sleep()
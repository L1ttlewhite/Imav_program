# -*- coding: UTF-8 -*-

import roslib
import rospy
import yaml, os, time
import smach
import smach_ros
import zbar
import numpy as np 
import cv2 as cv 
from PIL import Image
from Camera import Camera
from Window import Windowhandler
from geometry_msgs.msg import Point

#起飞定高程序
class Takeoff(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])

    def execute(self, userdata):
        rospy.loginfo('uav is taking off')
        global state_position_x, state_position_y, state_position_z, uav_position_pub
        uav_position = Point()
        uav_position.x = 0
        uav_position.y = 0
        uav_position.z = 0.5
        take_off_count = 0
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            uav_position_pub.publish(uav_position)
            if abs(state_position_z - 0.5) < 0.1:
                take_off_count += 1
            else:
                take_off_count = 0
            if take_off_count >= 30:
                return 'succeed'
            else:
                print 'taking off !!!!!!!!'
            rate.sleep()

#切换到寻找窗户飞航点的程序
class Window(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is detecting windows')
        global state_position_x, state_position_y, state_position_z, uav_position_pub
        current_path = os.path.abspath(os.path.dirname(__file__))
        with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
            camera_yaml = yaml.load(f.read())
            camera_fx   = camera_yaml['camera_fx']
            camera_fy   = camera_yaml['camera_fy'] 
            camera_bf   = camera_yaml['camera_bf']
            #camera_topic =camera_yaml['camera_topic']
            camera_topic_left = camera_yaml['camera_topic_left']
            camera_topic_right = camera_yaml['camera_topic_right']
            window_hsv_low = camera_yaml['window_hsv_low']
            window_hsv_high = camera_yaml['window_hsv_high']
        uav_position = Point()
        uav_position_f = Point()
        x,y,z = 0,0,0
        uav_position_f.x = 0
        uav_position_f.y = 0
        uav_position_f.z = 0
        window_L = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_left)    
        window_R = Windowhandler(mode = 1, video_num = 0, video_topic = camera_topic_right)
        while not rospy.is_shutdown():
            if window_L.isOpen() and window_R.isOpen():
                window_L.Process_image_HSV(HSV_low = window_hsv_low,HSV_high = window_hsv_high)
                window_R.Process_image_HSV(HSV_low = window_hsv_low,HSV_high = window_hsv_high)
                window_L.Get_contours()
                window_R.Get_contours()
                window_L.WindowFinding()
                window_R.WindowFinding()
                window_L.Show_contours_window('image_left')
                if window_L.isFind() and window_R.isFind():
                    x1,y1 = window_L.Get_centerid()
                    x2,y2 = window_R.Get_centerid()
                    
                    x,y,z = window_L.Stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bf)
            
                    uav_position.x = z/1000 + state_position_x  + 0.5
                    uav_position.y = -x/1000 + state_position_y + 0.13 
                    uav_position.z = -y/1000 + state_position_z 

                    #filter
                    uav_position_f.x = 0.7*uav_position_f.x + 0.3*uav_position.x 
                    uav_position_f.y = 0.7*uav_position_f.y + 0.3*uav_position.y 
                    uav_position_f.z = 0.7*uav_position_f.z + 0.3*uav_position.z

                    uav_position_pub.publish(uav_position_f)
                    print uav_position_f.x, uav_position_f.y, uav_position_f.z
        #Window_flag = True
        #if Window_flag:
        #    return 'succeed'
        #else: 
        #    return 'failure'

class Find_Line(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is finding a line')
        Find_Line_flag = True
        if Find_Line_flag:
            return 'succeed'
        else: 
            return 'failure'

class Follow_Line(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is flowing a line')
        Follow_Line_flag = True
        if Follow_Line_flag:
            return 'succeed'
        else: 
            return 'failure'

class Scan_QRCode(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is scaning QRCode')
        Scan_QRCode_flag = True
        if Scan_QRCode_flag:
            return 'succeed'
        else:
            return 'failure'

class Loop(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is crossing loops')
        Loop_flag = True
        if Loop_flag:
            return 'succeed'
        else: 
            return 'failure'

class Landing(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is crossing loops')
        Landing_flag = True
        if Landing_flag:
            return 'succeed'
        else: 
            return 'failure'



state_position_x, state_position_y, state_position_z = 0,0,0
def callback_position(Point):
    global state_position_x, state_position_y, state_position_z
    state_position_x = Point.x
    state_position_y = Point.y
    state_position_z = Point.z


rospy.init_node('IMAV_state_machine', anonymous = True)
rospy.Subscriber('state_position',Point,callback_position)
uav_position_pub = rospy.Publisher('uav_position', Point, queue_size=1)

sm = smach.StateMachine(outcomes = ['system_succeed', 'system_failure'])


#状态机
with sm:
    smach.StateMachine.add('Takeoff',Takeoff(),
                            transitions={'succeed':'Window',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Window',Window(),
                            transitions={'succeed':'Find_Line',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Find_Line',Find_Line(),
                            transitions={'succeed':'Follow_Line',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Follow_Line',Follow_Line(),
                            transitions={'succeed':'Scan_QRCode',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Scan_QRCode',Scan_QRCode(),
                            transitions={'succeed':'Loop',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Loop',Loop(),
                            transitions={'succeed':'Landing',
                                            'failure':'system_failure'})
    smach.StateMachine.add('Landing',Landing(),
                            transitions={'succeed':'system_succeed',
                                            'failure':'system_failure'})

sis = smach_ros.IntrospectionServer('IMAV_state_machine', sm, '/SM_ROOT')
sis.start()

outcome = sm.execute()

rospy.spin()
sis.stop()




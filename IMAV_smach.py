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

class Takeoff(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])

    def execute(self, userdata):
        rospy.loginfo('uav is taking off')
        takeoff_flag = True
        if takeoff_flag:
            return 'succeed'
        else: 
            return 'failure'

class Window(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeed','failure'])
    def execute(self, userdata):
        rospy.loginfo('uav is detecting windows')
        window_L = Windowhandler(mode = camera_mode, video_num = camera_video_num, 
                                    video_topic = camera_topic_left)    
        window_R = Windowhandler(mode = camera_mode, video_num = camera_video_num, 
                                    video_topic = camera_topic_right)
        while(True):
            window_L.Get_contours()
            window_R.Get_contours()
            window_L.WindowFinding()
            window_R.WindowFinding()
            window_L.Show_contours_window('image_left')
            window_R.Show_contours_window('image_right')
            if window_L.isFind() and window_R.isFind():
                x1,y1 = window_L.Get_centerid()
                x2,y2 = window_R.Get_centerid()
                x,y,z = window_L.Stereo_center(x1, y1, x2, y2, camera_fx, camera_fy, camera_bl)
            cv.waitKey(1)
            #差条件
            Window_flag = True
            if Window_flag:
                window_L.Release()
                window_R.Release()
                del window_L
                del window_R
                cv.destroyAllWindows()
                break
        if Window_flag:
            return 'succeed'
        else: 
            return 'failure'

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
        QRcamera = Camera(mode = camera_mode, video_num = camera_video_num, 
                                    video_topic = camera_topic_left)
        scanner = zbar.ImageScanner()
        # configure the reader
        scanner.parse_config('enable')  
        frame = QRcamera.Get_image_color()
        while(True):
            pil = Image.fromarray(frame).convert('L')
            width, height = pil.size
            #pil.show()
            raw = pil.tobytes()
            # wrap image data
            image = zbar.Image(width, height, 'Y800', raw)
            # scan the image for barcodes
            scanner.scan(image)
            tmpdata=''
            # extract results
            for symbol in image:
                # do something useful with results
                print symbol.type, '图片内容为:\n%s' % symbol.data
                tmpdata=tmpdata+symbol.data
                #差条件
                Scan_QRCode_flag = True
                if Scan_QRCode_flag:
                    del QRcamera
                    cv.destroyAllWindows()
                    break       
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


current_path = os.path.abspath(os.path.dirname(__file__))
with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
    camera_yaml = yaml.load(f.read())
    camera_fx   = camera_yaml['camera_fx']
    camera_fy   = camera_yaml['camera_fy'] 
    camera_bl   = camera_yaml['camera_bl']
    camera_topic =camera_yaml['camera_topic']
    camera_topic_left = camera_yaml['camera_topic_left']
    camera_topic_right = camera_yaml['camera_topic_right']
    window_hsv_low = camera_yaml['window_hsv_low']
    window_hsv_high = camera_yaml['window_hsv_high']
    camera_mode = camera_yaml['camera_mode']
    camera_video_num = camera_yaml['camera_video_num']




def main():
    rospy.init_node('IMAV_state_machine', anonymous = True)

    sm = smach.StateMachine(outcomes = ['system_succeed', 'system_failure'])

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



if __name__ =='__main__':
    main()
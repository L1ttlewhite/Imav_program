# -*- coding: UTF-8 -*-

import numpy as np 
import cv2 as cv
import roslib
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class Camera (object):

    # change mode to choose the way to get image. (video capture / topic subscribtion)
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw", image_path = ''):
        self.image_capture_flag = False
        self.video_num = video_num
        self.video_topic = video_topic
        self.bridge = CvBridge()
        if mode == 0:    
            self.capture = cv.VideoCapture(self.video_num)
        elif mode == 1:
            self.image_sub = rospy.Subscriber(self.video_topic, 
                                               Image, self.callback)
        elif mode == 2:
            print image_path
            self.image_color = cv.imread(image_path)
        elif mode == 3:
            self.capture = cv.VideoCapture(image_path)    
        else:
            print ('Wrong camera mode. Please choose 1 for video or 2 for topic or 3 for file or 4 for video file.')

    def Release(self):
        self.capture.release()

    # subscriber function callback to get image_color
    def callback(self, data):
        try:
            self.image_color = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.image_capture_flag = True
        except CvBridgeError as e:
            self.image_capture_flag = False
            print ('no image topic to subscribe')

    def isOpen(self):
        return self.image_capture_flag

    # get image from capture, should be used in while
    def Cap_image(self):
        if self.capture.isOpened():
            ret, self.image_color = self.capture.read()
            self.image_capture_flag = True
        else:
            self.image_capture_flag = False
            print ("Camera dev is not open")

    # process the image to get image_hsv, image_thre, image_gray
    def Process_image_HSV(self, HSV_low, HSV_high):
        # BGR Transform to HSV
        image_blur_1 = cv.GaussianBlur(self.image_color,(5,5),0)
        self.image_hsv = cv.cvtColor(image_blur_1, cv.COLOR_BGR2HSV)
    
        # Build the mask for the window
        image_mask = cv.inRange(self.image_hsv, HSV_low, HSV_high)
    
        # Bitwise operation
        image_res = cv.bitwise_and(self.image_color, self.image_color,
                                            mask = image_mask)
        image_blur_2 = cv.GaussianBlur(image_res,(5,5),0)
        # BGR to GRAY
        self.image_gray = cv.cvtColor(image_blur_2, cv.COLOR_BGR2GRAY)
        # Threshold
        ret, self.image_thre = cv.threshold(self.image_gray,0,255,
                                            cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
        self.image_thre = cv.morphologyEx(self.image_thre, cv.MORPH_OPEN, 
                                            kernel = np.ones((3,3), np.uint8))

    def Process_image_Thre(self, thre):
        self.image_gray = cv.cvtColor(self.image_color,cv.COLOR_BGR2GRAY)
        #这个函数，thre_new 代表阈值，255代表超过阈值后的像素的值，也可以修改第四个参数为cv2.THRESH_OTSU 使其自动二值化
        #黑线找出来，其余为白色
        gray_image = self.image_gray.copy()
        ret,thresh_window=cv.threshold(gray_image, thre, 255, cv.THRESH_BINARY)
        self.image_thre = cv.morphologyEx(thresh_window, cv.MORPH_OPEN, kernel = np.ones((3,3), np.uint8))

    # get the contours and hierarchy. the last two params can be changed to speed up
    def Get_contours(self):
        image_contours = self.image_thre.copy()
        image_contours[0:10,:] = 255
        image_contours[470:480,:] = 255
        image_contours[:,0:10] = 255
        image_contours[:,630:640] = 255
        image, self.contours, self.hierarchy = cv.findContours(image_contours,
                                        cv.RETR_TREE,cv.CHAIN_APPROX_NONE)
        #self.Show_image_thre()

    # some methods to show image
    def Show_contours(self):
        image_contours = self.image_color.copy()
        cv.drawContours(image_contours, self.contours, -1,
                                        (0,0,255), 3)
        cv.imshow('image_contours', image_contours)

    def Get_image_color(self):
        return self.image_color

    def Show_image_color(self, window_name = 'image_color'):
        cv.imshow(window_name, self.image_color)

    def Show_image_gray(self, window_name = 'image_gray'):
        cv.imshow(window_name, self.image_gray)

    def Show_image_hsv(self, window_name = 'image_hsv'):
        cv.imshow(window_name, self.image_hsv)

    def Show_image_thre(self, window_name = 'image_thre'):
        cv.imshow(window_name, self.image_thre)
                                            

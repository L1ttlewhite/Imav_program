# -*- coding: UTF-8 -*-

import numpy as np 
import cv2 as cv
from Camera import Camera




class Windowhandler(Camera):
    
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw"):
        #super(Windowhandler,self).__init__( mode = 0, video_num = 0, video_topic = "/image_raw")
        super(Windowhandler,self).__init__( mode, video_num, video_topic)
        self.max_area = 100000
        self.min_area = 50000
        

    def Centroid_drawer(self,x_weight,y_weight,weight):
        if weight:
            centroid_x = int(x_weight/weight)
            centroid_y = int(y_weight/weight)
            cv.circle(self.image_color,(centroid_x,centroid_y), 10, (0,0,255), -1)
            return centroid_x,centroid_y
        else:return 0,0

    def Find_center(self):
        self.center_x, self.center_y = 0,0
        self.x_weight = 0
        self.y_weight = 0
        self.weight   = 0
        self.contours_window = []
        for contour in self.contours:
            epsilon = 0.1*cv.arcLength(contour,True)
            approx = cv.approxPolyDP(contour,epsilon,True)
            if cv.contourArea(contour) >= self.min_area :
                if cv.contourArea(contour) <= self.max_area :
                    #self.image_color = cv.drawContours(self.image_color, contour, -1, (255,0,0), 3)
                    self.contours_window.append(contour)
                    M = cv.moments(contour)
                    self.x_weight = self.x_weight + int(M['m10'])
                    self.y_weight = self.y_weight + int(M['m01'])
                    self.weight = self.weight + int(M['m00'])
            # Draw center
            if self.x_weight:
                if self.y_weight:
                    self.center_x,self.center_y = self.Centroid_drawer(self.x_weight,
                                                    self.y_weight, self.weight)
                    #print(center_x, center_y)
    
    def Show_contours_window(self, window_name = 'image_contours_window'):
        image_contours_window = self.image_color
        cv.drawContours(image_contours_window, self.contours_window, -1,
                                        (0,0,255), 3)
        cv.imshow(window_name, image_contours_window)

    def Get_centerid(self):
        return self.center_x, self.center_y
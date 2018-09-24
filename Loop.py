import numpy as np 
import cv2 as cv
import math
from Camera import Camera



class Loophandler(Camera):  
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw", image_path = ''):
        super(Loophandler,self).__init__( mode, video_num, video_topic, image_path)
        self.Maxdistance = 100
        self.max_area = 200000
        self.min_area = 10000
        self.arearate = 0.65
        self.find_center_flag = False
        self.isLoop = False
        self.center_x, self.center_y = 0,0

    def Center_calculator(self,x_weight,y_weight,weight):
        if weight:
            center_x = int(x_weight/weight)
            center_y = int(y_weight/weight)
            return center_x,center_y
        else:return 0,0

    #找窗户的主函数
    def Loop_Find(self):
        self.contours_loop = []
        self.contours_area = []
        x_weight, y_weight = 0,0
        center = []
        for con in self.contours:
            contour_area = cv.contourArea(con)
            if contour_area >= self.min_area and contour_area <= self.max_area :
                (x,y), radius = cv.minEnclosingCircle(con)
                circlearea = math.pi * radius * radius
                rate = contour_area / circlearea
                if rate > self.arearate: 
                    M = cv.moments(con)
                    x_weight = int(M['m10'])
                    y_weight = int(M['m01'])
                    weight =  int(M['m00'])
                    # Draw center
                    if x_weight: 
                        if y_weight:
                            center_x,center_y = self.Center_calculator(x_weight,
                                                            y_weight, weight)
                            center.append(np.array([center_x,center_y]))
                            self.contours_area.append(contour_area)
                            self.contours_loop.append(con)
        return center


    def LoopFinding(self): 
        if len(self.contours) == 0:
            print ('no self.contours_loop in image')
            self.center_x = 0
            self.center_y = 0
            self.find_center_flag = False
        else:
            center = self.Loop_Find()
            if len(center) > 0 :
                self.find_center_flag = True 
                if len(center) == 1:    
                    self.center_x = center[0][0]
                    self.center_y = center[0][1]
                else:
                    idx = np.argmax(self.contours_area)
                    self.center_x = center[idx][0]
                    self.center_y = center[idx][1]          
            else:
                self.find_center_flag = False
                self.center_x = 0
                self.center_y = 0

    def isFind(self):
        return self.find_center_flag

    def Show_contours_window(self, window_name = 'image_contours_loop'):
        image_contours_loop = self.image_color.copy()
        cv.circle(image_contours_loop,(self.center_x,self.center_y), 10, (0,0,255), -1)
        cv.drawContours(image_contours_loop, self.contours_loop, -1,
                                        (0,0,255), 3)
        cv.imshow(window_name, image_contours_loop)
        #cv.waitKey(0)

    def Get_centerid(self):
        return self.center_x, self.center_y    
    
    def Stereo_center(self, x1, y1, x2, y2, fx, fy, bl):
        x,y,z = 0,0,0
        if x1 and y1 and x2 and y2:
            print abs(x1-x2)
            if abs(x1-x2) <= 50: 
                z = fx * bl / (x1 - x2)
                x = x1 * z / fx
                y = y1 * z / fy
        return x, y, z 
    
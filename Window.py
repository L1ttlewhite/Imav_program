# -*- coding: UTF-8 -*-

import numpy as np 
import cv2 as cv
import math
from Camera import Camera



class Windowhandler(Camera):
    
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw", image_path = ''):
        #super(Windowhandler,self).__init__( mode = 0, video_num = 0, video_topic = "/image_raw")
        super(Windowhandler,self).__init__( mode, video_num, video_topic, image_path)
        self.Maxdistance = 100
        self.max_area = 200000
        self.min_area = 3000
        self.Truetime = 0       
        self.center_x, self.center_y = 0,0
        self.find_center_flag = False
        self.isRectangle = False
        self.center_x_old, self.center_y_old = 0,0
        # define by XJ in his method
        self.center_filter_normal_x = []
        self.center_filter_normal_y = []
        self.center_filter_abnormal_x = []
        self.center_filter_abnormal_y = []     
        self.center_flag = 0
        self.Checktme = 0
        self.center_origin_x, self.center_origin_y = 0,0
        self.center_nowaday_x, self.center_nowaday_y = 0,0
        self.center_final_x, self.center_final_y = 0,0

    # 用图像矩来计算质心
    def Center_calculator(self,x_weight,y_weight,weight):
        if weight:
            center_x = int(x_weight/weight)
            center_y = int(y_weight/weight)
            return center_x,center_y
        else:return 0,0

    #判断矩形的方法来实现找窗户的中心
    #严格判断矩形，pt0-pt2为矩形任意三个定点，但对旋转的鲁棒性不强
    def Check_rectangle(self, center_x, center_y, pt0, pt2):
        #一个可调阈值，取大是为了，在方形旋转，变成菱形时可以正确检测出
        yuzhi = 50
        dx = abs(pt0[0]-pt2[0])
        dy = abs(pt0[1]-pt2[1])
        try:
            #判断所选轮廓外围是否为黑色，确定是否为窗户轮廓     
            check_num_1 = np.sum(self.image_thre[int(center_y+dy/2+yuzhi),int(center_x-dx/2-yuzhi):int(center_x+dx/2+yuzhi)])
            check_num_2 = np.sum(self.image_thre[int(center_y-dy/2-yuzhi),int(center_x-dx/2-yuzhi):int(center_x+dx/2+yuzhi)])
            check_num_3 = np.sum(self.image_thre[int(center_y-dy/2-yuzhi):int(center_y+dy/2+yuzhi),int(center_x+dx/2+yuzhi)])
            check_num_4 = np.sum(self.image_thre[int(center_y-dy/2-yuzhi):int(center_y+dy/2+yuzhi),int(center_x-dx/2-yuzhi)])  
        except:
            check_num_1 = 100
            check_num_2 = 100
            check_num_3 = 100
            check_num_4 = 100
            print 'error'
        
        print check_num_1, check_num_2, check_num_3, check_num_4
        #print self.image_thre[340][430], self.image_thre[430][340]
        if check_num_1 < 10 and check_num_2 < 10 and check_num_3 < 10 and check_num_4 <10:
            self.isRectangle = True
        else:
            self.isRectangle = False
    
    #测试发现矩形对旋转的鲁棒性不佳，采用外接圆来判断
    def checkcontour(self, con):
        (x,y), radius = cv.minEnclosingCircle(con)
        try:  
            #print x,y,radius
            #cv.waitKey(0)  
            check_num_1 = self.image_thre[y][x-radius]
            check_num_2 = self.image_thre[y][x+radius]
            check_num_3 = self.image_thre[int(y-radius/1.2)][x]
            check_num_4 = self.image_thre[int(y+radius/1.2)][x]
        except:
            check_num_1 = 100
            check_num_2 = 100
            check_num_3 = 100
            check_num_4 = 100
            print 'error'
            
        #print check_num_1, check_num_2, check_num_3, check_num_4
        #print self.image_thre[340][430], self.image_thre[430][340]
        if check_num_1 == 0 and check_num_2 == 0 and check_num_3 == 0 and check_num_4 == 0:
            #print x,y,radius
            #cv.waitKey(0)
            self.isRectangle = True
        else:
            self.isRectangle = False

    #找窗户的主函数
    def Window_Find(self, delta = 0.7, epsilon = 0.01, minangle = 80, maxangle = 100):
        self.contours_window = []
        x_weight, y_weight = 0,0
        center = []
        for con in self.contours:
            if cv.contourArea(con) >= self.min_area :
                if cv.contourArea(con) <= self.max_area :
                    approx = cv.approxPolyDP(con, epsilon * cv.arcLength(con, True), True)
                    # if shape is a rectangle approx.shape = (4,1,2)
                    if approx.shape[0] == 4:
                            #center.append(self.center(approx[i%4][0], approx[i-1][0], approx[i-2][0]))
                        M = cv.moments(con)
                        x_weight = int(M['m10'])
                        y_weight = int(M['m01'])
                        weight =  int(M['m00'])
                        # Draw center
                        if x_weight:
                            if y_weight:
                                center_x,center_y = self.Center_calculator(x_weight,
                                                                y_weight, weight)
                                #self.Check_rectangle(center_x, center_y, approx[0][0], approx[2][0])
                                self.checkcontour(con)
                                if self.isRectangle:
                                    center.append(np.array([center_x,center_y]))
                                    self.contours_window.append(con)
                                #else:
                                    #print approx
                            #else:
                            #    self.find_center_flag = False
        return self.contours_window, center


    def WindowFinding(self): 
        if len(self.contours) == 0:
            print ('no self.contours_window in image')
            self.center_x = 0
            self.center_y = 0
            self.find_center_flag = False
        else:
            self.contours_window, center = self.Window_Find()
            #print len(self.contours_window),center,len(center)
            if len(center) > 0 :
                self.find_center_flag = True 
                if len(center) == 1:    
                    self.center_x = center[0][0]
                    self.center_y = center[0][1]
                    #print self.center_x,self.center_y 
                else:
                    center_sum = np.zeros(len(center))
                    for i in range(len(center_sum)):
                        center_sum[i] = abs(center[i][0]) + abs(center[i][1]-240)
                    idx = np.argmax(center_sum)
                    self.center_x = center[idx][0]
                    self.center_y = center[idx][1]          
                #print ('the center of self.contours_window is  : {}'.format(center))
            else:
                self.find_center_flag = False
                self.center_x = 0
                self.center_y = 0


    def isFind(self):
        return self.find_center_flag

    def Distance(self, x1, y1, x2, y2):
        return ((x1 - x2)**2 + (y1 - y2)**2)

    def Show_contours_window(self, window_name = 'image_contours_window'):
        image_contours_window = self.image_color
        cv.circle(image_contours_window,(self.center_x,self.center_y), 10, (0,0,255), -1)
        cv.drawContours(image_contours_window, self.contours_window, -1,
                                        (0,0,255), 3)
        cv.imshow(window_name, image_contours_window)
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
    
    
    








'''
    #not used
    #以下代码在算全局的轮廓矩，上面的是基于提取颜色框，找中间的框的算法
    def Find_center(self): 
        x_weight = 0
        y_weight = 0
        weight   = 0
        self.contours_window = []
        for contour in self.contours:
            epsilon = 0.1*cv.arcLength(contour,True)
            approx = cv.approxPolyDP(contour,epsilon,True)
            if cv.contourArea(contour) >= self.min_area :
                if cv.contourArea(contour) <= self.max_area :
                    self.image_color = cv.drawContours(self.image_color, contour, -1, (255,0,0), 3)
                    self.contours_window.append(contour)
                    M = cv.moments(contour)
                    x_weight = x_weight + int(M['m10'])
                    y_weight = y_weight + int(M['m01'])
                    weight = weight + int(M['m00'])
            # Draw center
            if x_weight:
                if y_weight:
                    self.center_x,self.center_y = self.Center_calculator(x_weight,
                                                    y_weight, weight)
                    if self.Truetime >= 3:
                        if self.Distance(self.center_x, self.center_y, 
                                self.center_x_old, self.center_y_old) < self.Maxdistance:
                            self.center_x = ( self.center_x + self.center_x_old ) / 2
                            self.center_y = ( self.center_y + self.center_y_old ) / 2 
                            self.find_center_flag = True
                        self.Truetime = 0
                    
                    else:
                        self.find_center_flag = False
                    self.center_x_old = self.center_x
                    self.center_y_old = self.center_y
                    self.Truetime = self.Truetime + 1 
            self.Checktme = self.Checktme + 1 
    
    # method by XJ 
    def Filter(self):
        if self.Checktme >=5 and self.center_x:
            length_normal = len(self.center_filter_normal_x)
            length_abnormal = len(self.center_filter_abnormal_x)
   
            # Judgement
            if self.center_flag == 0:
                self.center_flag = 1
                self.center_origin_x = self.center_x
                self.center_origin_y = self.center_y
            elif self.center_flag == 1:
                self.center_nowaday_x = self.center_x
                self.center_nowaday_y = self.center_y
                if distance(self.center_origin_x, self.center_origin_y, self.center_nowaday_x, self.center_nowaday_y) < self.Maxdistance:
                    self.center_filter_normal_x.append(self.center_nowaday_x)
                    self.center_filter_normal_y.append(self.center_nowaday_y)
                else :
                    self.center_filter_abnormal_x.append(self.center_nowaday_x)
                    self.center_filter_abnormal_y.append(self.center_nowaday_y)
                if length_abnormal <= 2 and length_normal == 10:
                    self.center_flag = 2
                    self.center_final_x = int(sum(self.center_filter_normal_x)/(length_normal+1))
                    self.center_final_y = int(sum(self.center_filter_normal_y)/(length_normal+1))
                elif length_abnormal >= 10 and length_normal <= 2:
                    self.center_flag = 0
                elif length_abnormal >=10 and length_normal >= 10:
                    self.center_flag = 3
                else:
                    self.center_flag = 0
            # Job done, return value
            elif self.center_flag == 2:
                self.center_x = self.center_final_x
                self.center_y = self.center_final_y
            # I think the most excetutable method is move the plane
            elif self.center_flag == 3:
                self.center_flag = 0
                del self.center_filter_abnormal_x[:]
                del self.center_filter_abnormal_y[:]
                del self.center_filter_normal_x[:]
                del self.center_filter_normal_y[:]


    #调试用，分步显示图中轮廓，×××未测试运行××××
    def Show_contours_window_step(self, window_name = 'image_contours_window_step'):
        image_contours_window_step = self.image_color
        for contour_window in self.contours_window:
            print contour_window
            cv.drawContours(image_contours_window_step, contour_window, -1,
                                    (0,0,255), 3)
            M = cv.moments(contour)
            x_weight = x_weight + int(M['m10'])
            y_weight = y_weight + int(M['m01'])
            weight = weight + int(M['m00'])
            # Draw center
            if x_weight:
                if y_weight:
                    center_x,center_y = self.Center_calculator(x_weight,
                                                    y_weight, weight)
            cv.circle(image_contours_window_step, (center_x, center_y), 10
                            (0,0,255), -1)
            cv.imshow(window_name, image_contours_window_step)
'''
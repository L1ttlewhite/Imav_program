# -*- coding: UTF-8 -*-

import numpy as np 
import cv2 as cv
import math
from Camera import Camera

class Linehandler(Camera):
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw", image_path = ''):
        #super(Windowhandler,self).__init__( mode = 0, video_num = 0, video_topic = "/image_raw")
        super(Linehandler,self).__init__( mode, video_num, video_topic, image_path)
        self.ROI_h = 20
        '''
        self.ROIS = [[0,450,640,self.ROI_h,8],
                    [0,380,640,self.ROI_h,7],
                    [0,310,640,self.ROI_h,6],
                    [0,240,640,self.ROI_h,5],
                    [0,210,640,self.ROI_h,4],
                    [0,140,640,self.ROI_h,3],
                    [0,70,640,self.ROI_h,2],
                    [0,0,640,self.ROI_h,1]]    #[x,y,w,h,index]
        '''
        self.ROIS = [[0,460,640,self.ROI_h,12],
                    [0,440,640,self.ROI_h,11],
                    [0,420,640,self.ROI_h,10],
                    [0,400,640,self.ROI_h,9],
                    [0,380,640,self.ROI_h,8],
                    [0,360,640,self.ROI_h,7],
                    [0,340,640,self.ROI_h,6],
                    [0,320,640,self.ROI_h,5],
                    [0,300,640,self.ROI_h,4],
                    [0,280,640,self.ROI_h,3],
                    [0,260,640,self.ROI_h,2],
                    [0,240,640,self.ROI_h,1],
                    [0,220,640,self.ROI_h,12],
                    [0,200,640,self.ROI_h,11],
                    [0,180,640,self.ROI_h,10],
                    [0,160,640,self.ROI_h,9],
                    [0,140,640,self.ROI_h,8],
                    [0,120,640,self.ROI_h,7],
                    [0,100,640,self.ROI_h,6],
                    [0,80,640,self.ROI_h,5],
                    [0,60,640,self.ROI_h,4],
                    [0,40,640,self.ROI_h,3],
                    [0,20,640,self.ROI_h,2],
                    [0,0,640,self.ROI_h,1]]    #[x,y,w,h,index]
        self.blobs = []
        self.scale = 0

    def Scale_cal(self, len_of_line = 0):
        #用来确定巡线的尺度，结合线的像素值和实际长度
        pass 

    def Find_blobs(self, blob_w = 2):
        blob_h = 0.5 * self.ROI_h
        blob  = []
        self.blobs = []
        blob_start = 0
        blob_end   = 0
        blob_find  = False
        for roi in self.ROIS:
            image_thre = self.image_thre/255
            roi_img = image_thre[roi[1]:(roi[1]+roi[3]),roi[0]:roi[2]]
            #cv.imshow('roi',roi_img)
            #cv.waitKey(0)
            #roi 区域中每一列的像素值的和
            roi_img_col = roi_img.sum(axis=0)
            #print roi_img_col
            for i in range(len(roi_img_col)):
                if blob_find : 
                    if roi_img_col[i] > blob_h:
                        blob_end = i
                        if (blob_end - blob_start) > blob_w :
                            blob.append([blob_start, (blob_end - blob_start + 1), roi[1]])
                        blob_find = False
                else:
                    if roi_img_col[i] < blob_h:
                        blob_find = True
                        blob_start = i
            if blob:
                self.blobs.append(blob) #blob [start, length, ]
            blob = []
        #print self.blobs    

    def Draw_blobs(self):
        if self.blobs:
            print self.blobs
            image_blobs = self.image_color.copy()
            for i in self.blobs:
                for j in i : 
                    print         
                    cv.rectangle(image_blobs, (j[0],j[2]), ((j[0]+j[1]),j[2]+self.ROI_h),(0,0,255),3)
            cv.imshow('image_blobs', image_blobs)
    
    #返回中心
    def _center_blob(self, blob):
        center = [int(blob[2]+25), int(blob[0]+blob[1]/2)]
        return center
    
    #确定两个blob之间的点是否为黑点，直线检测时的检测步骤
    def _check_block(self, center_new, center_old, block_size = 1):
        center = [(center_old[0]-center_new[0]), (center_old[1]-center_new[1])]
        img_check = self.image_thre[(center_old[0]-center[0]/2-block_size/2):(center_old[0]-center[0]/2+block_size/2),
                            (center_old[1]-center[1]/2-block_size/2):(center_old[1]-center[1]/2+block_size/2)]
        
        #cv.imshow('img_check',img_check)
        #cv.waitKey(0)
        #print img_check.sum()
        check_flag = ( img_check.sum() == 0  )
        return check_flag
    
    #找直线
    def Find_line (self):
        line = []
        max_firstblob = 0
        for i in range(len(self.blobs)):
            if i == 0 :
                if len(self.blobs[0]) > 1:
                    #找到最低端黑块中长度最长的那一块
                    for j in self.blobs[0]:
                        if j[1] > max_firstblob:
                            max_firstblob = j[1]
                    for j in self.blobs[0]:
                        if j[1] < max_firstblob:
                            self.blobs[0].remove(j)
                    center_old = self._center_blob(self.blobs[0][0])
                else:
                    center_old = self._center_blob(self.blobs[0][0])
                line.append(center_old)
            else:
                for j in self.blobs[i]:
                    center_new = self._center_blob(j)
                    if self._check_block(center_new,center_old):
                        line.append(center_new)
                        center_old = center_new
        return line
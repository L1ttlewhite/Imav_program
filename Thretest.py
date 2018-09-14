# -*- coding: utf-8 -*-
# This code is for find the best threshold value for the method

import cv2
import numpy as np
# This function is used for nothing, but can't be deleted!
def nothing(x):
    pass

# Setting default value
thre_new = 0
thre_old = 1



# Set camera
camera1 = cv2.VideoCapture(1)

cv2.namedWindow('image', cv2.WINDOW_NORMAL)

cv2.createTrackbar('Thre', 'image', 0, 255, nothing)
while(1):
    # Get the image
    ret,frame_1 = camera1.read()
    #blur_1 = cv2.GaussianBlur(frame_1,(5,5),0)
    gray_1 = cv2.cvtColor(frame_1,cv2.COLOR_BGR2GRAY)
    #这个函数，thre_new 代表阈值，255代表超过阈值后的像素的值，也可以修改第四个参数为cv2.THRESH_OTSU 使其自动二值化
    ret,thresh_window=cv2.threshold(gray_1, thre_new, 255, cv2.THRESH_BINARY)
    thresh_window = cv2.morphologyEx(thresh_window, cv2.MORPH_OPEN, kernel = np.ones((3,3), np.uint8))
    cv2.imshow('image_raw', frame_1)
    cv2.imshow('image',thresh_window)
    # Get the value from the track bar
    thre_new = cv2.getTrackbarPos('Thre','image')
    if thre_new != thre_old: 
        # Print value
        print('Thre_low = %d' %(thre_new))
        
    thre_old = thre_new
    
    # Manual breakpoint
    k=cv2.waitKey(1)&0xFF
    if k==27:break

# Destroy all the windows
cv2.destroyAllWindows()

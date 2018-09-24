# -*- coding: utf-8 -*-
# This code is for find the best value for color in the HSV mode
# You can have the value and put this in your mask which used for main function
# This can't used for Mac 10.13.2 which python version is 3.6.6 for unknown reason
# Created by Xavier

import cv2
import numpy as np
# This function is used for nothing, but can't be deleted!
def nothing(x):
    pass
# Setting default value
h_low_new = 0
s_low_new = 0
v_low_new = 0
h_high_new = 0
s_high_new = 0
v_high_new = 0

h_low_old = 1
s_low_old = 1
v_low_old = 1
h_high_old = 1
s_high_old = 1
v_high_old = 1
# Set camera
camera1 = cv2.VideoCapture(0)

#frame_1 = cv2.imread('data/loop2.png')

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
# Create Trackbar
cv2.createTrackbar('H LOW','image',0,255,nothing)
cv2.createTrackbar('S LOW','image',0,255,nothing)
cv2.createTrackbar('V LOW' ,'image',0,255,nothing)
cv2.createTrackbar('H HIGH','image',0,255,nothing)
cv2.createTrackbar('S HIGH','image',0,255,nothing)
cv2.createTrackbar('V HIGH' ,'image',0,255,nothing)

while(1):
    # Get the image
    ret,frame_1 = camera1.read()
    # Set the mask value, both bottom and top
    window_bottom = np.array([h_low_new,s_low_new,v_low_new])
    window_top = np.array([h_high_new,s_high_new,v_high_new])
    # BGR Transform to HSV
    #blur_1 = cv2.GaussianBlur(frame_1,(5,5),0)
    hsv_1 = cv2.cvtColor(frame_1,cv2.COLOR_BGR2HSV)
    # Build the mask for the window
    mask_window = cv2.inRange(hsv_1,window_bottom,window_top)
    # Bitwise operation
    res_window = cv2.bitwise_and(frame_1,frame_1,mask = mask_window)
    #blur_window = cv2.GaussianBlur(res_window,(5,5),0)
    # BGR to GRAY
    gray_window = cv2.cvtColor(res_window, cv2.COLOR_BGR2GRAY)
    # Threshold
    ret,thresh_window=cv2.threshold(gray_window,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    thresh_window = cv2.morphologyEx(thresh_window, cv2.MORPH_OPEN, kernel = np.ones((3,3), np.uint8))
    cv2.imshow('image_raw', frame_1)
    cv2.imshow('image',thresh_window)
    # Get the value from the track bar
    h_low_new = cv2.getTrackbarPos('H LOW','image')
    s_low_new = cv2.getTrackbarPos('S LOW','image')
    v_low_new = cv2.getTrackbarPos('V LOW','image')
    h_high_new = cv2.getTrackbarPos('H HIGH','image')
    s_high_new = cv2.getTrackbarPos('S HIGH','image')
    v_high_new = cv2.getTrackbarPos('V HIGH','image')
    if h_low_new != h_low_old or s_low_new != s_low_old or v_low_new != v_low_old or h_high_new != h_high_old or s_high_new != s_high_old or v_high_new != v_high_old:
        # Print value
        print('H Low = %d'%(h_low_new))
        print('S Low = %d'%(s_low_new))
        print('V Low = %d'%(v_low_new))
        print('H High = %d'%(h_high_new))
        print('S High = %d'%(s_high_new))
        print('V High = %d'%(v_high_new))
    h_low_old = h_low_new
    s_low_old = s_low_new
    v_low_old = v_low_new
    h_high_old = h_high_new
    s_high_old = s_high_new
    v_high_old = v_high_new
    
    # Manual breakpoint
    k=cv2.waitKey(1)&0xFF
    if k==27:break

# Destroy all the windows
cv2.destroyAllWindows()

# -*- coding: UTF-8 -*-
import time
import yaml,os
import rospy 
import cv2 as cv
import numpy as np 
from Camera import Camera
from Line import Linehandler
from matplotlib import pyplot as plt
import math

imgwidth=160
imgheight=120
leftbound=[0 for i in range (imgheight)]
upbound=[0 for i in range (imgwidth)]
test=[0 for i in range (imgwidth)]
linehead=0
linetail=0
rowstart=5
rowend=116
colstart=40
colend=156
cntcir=0
mincencir=6


uav_pose = []


def getcencir(i,j):
    cencir=0
    cenrow=[0 for k in range  (5)]
    cenrow[2] =5-(int(img[i][j])+int(img[i][j+1])+int(img[i][j+2])+int(img[i][j-1])+int(img[i][j-2]))/255
    cenrow[1] =5-(int(img[i+1][j])+int(img[i+1][j+1])+int(img[i+1][j+2])+int(img[i+1][j-1])+int(img[i+1][j-2]))/255
    cenrow[3] =5-(int(img[i-1][j])+int(img[i-1][j+1])+int(img[i-1][j+2])+int(img[i-1][j-1])+int(img[i-1][j-2]))/255
    cenrow[0] =3-(int(img[i+2][j])+int(img[i+2][j+1])+int(img[i+2][j-1]))/255
    cenrow[4] =3-(int(img[i-2][j])+int(img[i-2][j+1])+int(img[i-2][j-1]))/255
    cencir=(cenrow[0]+cenrow[1]+cenrow[2]+cenrow[3]+cenrow[4]) 
    return cencir




def leftBlack_Extract(start,end):
    leftbound=[0 for i in range (imgheight)]
    linehead=0
    linetail=0
    rowstart=5
    rowend=116

    colstart=40
    colend=156
    global leftk 
    leftk=0

    for i in range (rowstart,rowend):
        for j in range (colstart,colend):
            flag1=0
            flag2=0
            cencir=0
            
            
            if ((img[i][j+1]==0 and img[i][j-2]==255)and(img[i][j+2]==0 and img[i][j-1]==255)):                
                cencir=getcencir(i,j)
                if(cencir>=mincencir):
                    if(linehead==0):
                        linehead=i
                    
                    leftbound[i]=j
                    #imgcolor[i][leftbound[i]]=(0,0,255)
                    #imgcolor[i][leftbound[i]-2]=(0,0,255)
                    #imgcolor[i][leftbound[i]+2]=(0,0,255)

                    #print cenrow
                    break
    
    for l in range (2,imgheight):
        if((leftbound[l-5]>0)and(leftbound[l-3]>0)and(leftbound[l-1]>0)and(leftbound[l]>0)and(leftbound[l+1]==0)):
            linetail=l
            break
            
    #print linehead,leftbound[linehead] ,linetail,leftbound[linetail]
    
    st=0
    ed=0
    if((linetail-linehead)>=20):
        st=linehead+int((linetail-linehead)/3)
        ed=linetail-int((linetail-linehead)/3)
    else:
        st=linehead
        ed=linetail

    for i in range(10):
        if(leftbound[st]>0):
            break
        else:
            st=st+1

    for i in range(10):
        if(leftbound[ed]>0):
            break
        else:
            ed=ed-1

    cv.line(imgcolor,(leftbound[st],st),(leftbound[ed],ed),(255,0,0),3)
    #cv.circle(imgcolor,(60,80),1,(0,0,255),3)

    #print st , leftbound[st] ,ed,leftbound[ed]
    
    
    
    leftk=-float(ed-st)/(float(leftbound[ed]-leftbound[st])+0.001)

    #leftk=float(ed-st)/float(leftbound[ed]-leftbound[st])
    #imgline=cv.resize(imgcolor,None,fx=4,fy=4,interpolation=cv.INTER_CUBIC)
    imgline=cv.resize(imgcolor,None,fx=4,fy=4,interpolation=cv.INTER_CUBIC)
    cv.circle(imgline,(320,240),3,(0,0,255),6)
    #imgline=imgcolor
    cv.imshow('imgline',imgline)

    return leftk
    


    
   
def upBlack_Extract(start,end):
    upbound=[0 for i in range (imgwidth)]
    linehead=0
    linetail=0
    rowstart=5
    rowend=116

    colstart=5
    colend=156
    global upk 
    upk=0
    
    for j in range (colstart,colend):
        for i in range (rowstart,rowend):
            flag1=0
            flag2=0
            cencir=0
            
            
            if ((img[i+1][j]==0 and img[i-2][j]==255)and(img[i+2][j]==0 and img[i-1][j]==255)):                
                cencir=getcencir(i,j)
                if(cencir>=mincencir):
                    if(linehead==0):
                        linehead=j
                    
                    upbound[j]=i
                    #imgcolor[upbound[j]][j]=(0,0,255)
                    #imgcolor[upbound[j]+2][j]=(0,0,255)
                    #imgcolor[upbound[j]-2][j]=(0,0,255)

                    #print cenrow
                    break

    #print upbound 
    for l in range (linehead,imgwidth):
        if((upbound[l-4]==0)and(upbound[l-2]==0)and(upbound[l]>0)and(upbound[l+4]>0)and(upbound[l+7]>0)):
            linehead=l
            break
    for l in range (5,imgwidth):
        if((upbound[l-5]>0)and(upbound[l-3]>0)and(upbound[l-1]>0)and(upbound[l]>0)and(upbound[l+1]==0)):
            linetail=l
            break
            
    #print linehead,linetail   
    st=0
    ed=0
    if((linetail-linehead)>=20):
        st=linehead+int((linetail-linehead)/3)
        ed=linetail-int((linetail-linehead)/3)
    else:
        st=linehead
        ed=linetail

    for i in range(10):
        if(upbound[st]>0):
            break
        else:
            st=st+1

    for i in range(10):
        if(upbound[ed]>0):
            break
        else:
            ed=ed-1

    cv.line(imgcolor,(st,upbound[st]),(ed,upbound[ed]),(255,0,0),3)
    
    
    upk=-float(upbound[ed]-upbound[st])/(float(ed-st)+0.001)
   

    imgline=cv.resize(imgcolor,None,fx=4,fy=4,interpolation=cv.INTER_CUBIC)
    cv.circle(imgline,(320,240),3,(0,0,255),6)
    #imgline=imgcolor
    cv.imshow('imgline',imgline)
    
    return upk
    



def getleftlen():
    global leftlen
    global leftlenrate
    leftlenrate=0
    leftlen=0
    for i in range (3,imgheight-3):
        
        for j in range (3,imgwidth-3):
                        
            if ((img[i][j+1]==0 and img[i][j-2]==255)and(img[i][j+2]==0 and img[i][j-1]==255)):      
                leftlen+=1          
                break

    leftlenrate=float(leftlen)/float(imgheight-6)



def getuplen():
    global uplenrate
    global uplen
    uplenrate=0
    upen=0
    for j in range (3,imgwidth-3):
        
        for i in range (3,imgheight-3):
                        
            if ((img[i+1][j]==0 and img[i-2][j]==255)and(img[i+2][j]==0 and img[i-1][j]==255)):      
                uplen+=1          
                break
    uplenrate=float(uplen)/float(imgwidth-6)


#左：0 右：1   上：0 下：1 平：2
current_state = {'left_right': 0, 'top_bot':0 }

def get_rate_state(rate):
    if abs(rate) < 0.2:
        return 0  
    elif rate < 0:
        return -1
    elif rate > 0:
        return 1   

def change_state(rate, current_state) :
    rate_state = get_rate_state(rate)
    #状态 左上
    if current_state['left_right'] == 0 and current_state['top_bot'] == 0:
        if rate_state == 0:
            current_state['top_bot'] = 2
            return current_state
        if rate_state < 0 :
            return current_state
        if rate_state > 0 :
            current_state['left_right'] = 1
            return current_state 
    #状态 左下        
    if current_state['left_right'] == 0 and current_state['top_bot'] == 1:
        if rate_state == 0:
            current_state['top_bot'] = 2
            return current_state
        if rate_state < 0 :
            current_state['left_right'] = 1
            return current_state
        if rate_state > 0 :         
            return current_state 
    #状态 左平
    if current_state['left_right'] == 0 and current_state['top_bot'] == 2:
        if rate_state == 0:
            return current_state
        if rate_state < 0 :
            current_state['top_bot'] = 0
            return current_state
        if rate_state > 0 :
            current_state['top_bot'] = 1
            return current_state 
    #状态 右上
    if current_state['left_right'] == 1 and current_state['top_bot'] == 0:
        if rate_state == 0:
            current_state['left_right'] = 0
            current_state['top_bot'] = 2
            return current_state
        if rate_state < 0 :
            current_state['left_right'] = 0
            return current_state
        if rate_state > 0 :
            return current_state 
    #状态 右下
    if current_state['left_right'] == 1 and current_state['top_bot'] == 1:
        if rate_state == 0:
            current_state['left_right'] = 0
            current_state['top_bot'] = 2
            return current_state
        if rate_state < 0 :   
            return current_state
        if rate_state > 0 :
            current_state['left_right'] = 0
            return current_state 
    #状态 右平
    if current_state['left_right'] == 1 and current_state['top_bot'] == 2:
        if rate_state == 0: 
            return current_state
        if rate_state < 0 :
            current_state['top_bot'] = 1
            return current_state
        if rate_state > 0 :
            current_state['top_bot'] = 0
            return current_state 



current_path = os.path.abspath(os.path.dirname(__file__))



thre = 80
path = current_path + '/data/' + 'test_video_1.avi'

rate_k_old = 0 
deg=0
delx=0
dely=0

#Line = Linehandler(mode = 0,  video_num = 0, video_topic = '', image_path = path)
#Line = Linehandler(mode = 0,  video_num =output.avi , video_topic = '', image_path = path)
cap = cv.VideoCapture('output.avi')
#cap = cv.VideoCapture(1)
while True:
    #Line.Cap_image()
    
    start_time  = time.time()
    uplen=0

    ratek=0
    
    ret, frame = cap.read()
    img=frame
    #cv.imshow('img',img)
    img=cv.resize(img,None,fx=0.25,fy=0.25,interpolation=cv.INTER_AREA)
    imgcolor=img

    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    #cv.imshow('gray',gray)
    blur = cv.blur(gray,(5,5))
    #cv.imshow('blur',blur)
    ret,thresh=cv.threshold(blur, thre, 255, cv.THRESH_BINARY)
    cv.imshow('thresh',thresh)
    img=thresh
    getleftlen()  
    getuplen()
    #print leftlen,leftlenrate,uplen,uplenrate

    if(leftlenrate>=uplenrate):
        ratek=leftBlack_Extract(start=colstart,end=colend)
    else:
        ratek=upBlack_Extract(start=rowstart,end=rowend)
    #leftBlack_Extract(start=colstart,end=colend)
    #upBlack_Extract(start=rowstart,end=rowend)
    #if ratek:
    #    rate_changing = ratek - rate_k_old
    #    rate_k_old = ratek
    end_time = time.time()
    current_state = change_state(ratek, current_state)
    #print ('the line rate is {}'.format(ratek)) 

    

    deg=math.atan(ratek)
    deg=math.degrees(deg)

    if((current_state['left_right'] == 0)):
        deg+=180
    elif((current_state['left_right'] == 1)and(current_state['top_bot'] == 1)):
        deg+=360


    #print ratek,deg

    deg=deg/180*3.14159

    dely=-2*math.cos(deg)
    delx=2*math.sin(deg)

    print delx,dely



    #print ('the changing rate is {}'.format(rate_changing))
    #print end_time - start_time
    #print current_state
    #print current_state['top_bot']


    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    

cap.release()
cv.destroyAllWindows()



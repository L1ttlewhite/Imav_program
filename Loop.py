import numpy as np 
import cv2 as cv
from Camera import Camera



class Windowhandler(Camera):
    
    def __init__(self, mode = 0, video_num = 0, video_topic = "/image_raw"):
        #super(Windowhandler,self).__init__( mode = 0, video_num = 0, video_topic = "/image_raw")
        super(Windowhandler,self).__init__( mode, video_num, video_topic)
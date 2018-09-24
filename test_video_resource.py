#! /usr/bin/env python2
# -*- coding: utf-8 -*-
"""

Copyright (c) 2015 PAL Robotics SL.
Released under the BSD License.

Created on 7/14/15

@author: Sammy Pfeiffer

test_video_resource.py contains
a testing code to see if opencv can open a video stream
useful to debug if video_stream does not work
"""

import sys
import signal
import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Point
import socket
import numpy as np
from threading import Thread, Lock
import time
import math
import threading
from numpy import uint8
from pylab import *




# if __name__ == '__main__':
#     # 参数的长度
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print "Error opening resource: " + str(resource)
#         exit(0)
#     bridge = CvBridge()
#     publisher = rospy.Publisher('image_topic', Image, queue_size=10)
#     rospy.init_node('web_cam')
#     print "Correctly opened resource, starting to show feed."
#     rval, frame = cap.read()

#     while rval:
#         # 将opencv格式的图片转换为ROS可接受的msg
#         image_message = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
#         try:
#             publisher.publish(image_message)
#         except CvBridgeError as e:
#             print(e)
#         rval, frame = cap.read()


#if(len(sys.argv) != 3):
#    print("Usage : {} hostname port".format(sys.argv[0]))
#    print("e.g.   {} 192.168.0.39 1080".format(sys.argv[0]))
#    sys.exit(-1)

#host = sys.argv[1]
#port = int(sys.argv[2])

# Create a UDP socket
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockTrans1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockTrans2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverip1 = '192.168.4.102'
serverport1 = 1082
server_address1 = (serverip1, serverport1)

serverip2 = '192.168.0.107'
serverport2 = 1082
server_address2 = (serverip2, serverport2)


clientip1 = '127.0.0.1'
clientip1 = '192.168.4.100'
clientport1 = 1084
client_address1 = (clientip1, clientport1)
sock1.bind(client_address1)

clientip2 = '127.0.0.1'
clientip2 = '192.168.0.100'
clientport2 = 1085
client_address2 = (clientip2, clientport2)
sock2.bind(client_address2)

running = True


class VideoReceiver(Thread):
    def __init__(self, sock):
        """Constructor."""
        Thread.__init__(self)
        self.running = True
        self.buffer = None
        self.array = None
        self.lock = Lock()
        self.frame = 0
        self.len = 0
        self.sock = sock
        self.errCount = 0
        self.time0 = time.time()
        if self.sock == sock1:
            self.name = 'Rec1'
        else:
            self.name = 'Rec2'
    def stop(self):
        self.running = False

    def get_frame(self):
        """Method to access the encoded buffer."""
        if self.array is not None:
            #self.lock.acquire()
            cpy = self.array.copy()
            frame_cpy = self.frame
            #self.lock.release()
            return cpy, frame_cpy
        else:
            return None, -1

    def run(self):
        while self.running:
            data, server = self.sock.recvfrom(65507)
            errFlag = False
            self.buffer = None
            
            if len(data) == 4:
                self.len = ord(data[0]) * 256 * 256 * 256 + ord(data[1]) * 256 * 256 + ord(data[2]) * 256 + ord(data[3])
                packageNum = math.ceil(self.len / 65400.0)
                #print(self.len / 65400.0)
                n = 0
                if packageNum < 20 and packageNum > 0:
                    while n < packageNum:
                        magic = np.array([[153], [214], [52], [16]], dtype=uint8)
                        data, server = self.sock.recvfrom(65507)
                        #print("len(self.data)", len(data), data[-4:], magic.tobytes(), data[0:4]==magic.tobytes())
                        if(data[0:4]!=magic.tobytes() or data[-4:]!=magic.tobytes()):
                            errFlag = True
                            print("RECEIVE ERROR")
                            break
                        if n == 0:
                            self.buffer = data[4:-4]
                            #print(len(data[4:-4]))
                        else:
                            self.buffer = self.buffer + data[4:-4]
                        n = n + 1
                else:
                    errFlag = True
                #data1, server = self.sock.recvfrom(65507)
                # JPEG compression
                # Protected by a lock
                # As the main thread may asks to access the buffer
                packInterval = (time.time() - self.time0)*1000
                self.time0 = time.time()
                if self.buffer == None:
                    bufferLen = 0
                else:
                    bufferLen = len(self.buffer)
                ####print(self.name, "Size:{}".format(bufferLen), 'Frame:',self.frame, 'errCount:',self.errCount, "errFlag:",errFlag, 'packInterval:',packInterval)
                if not errFlag:
                    if len(self.buffer) == self.len + 4:
                        frame0 = ord(self.buffer[-4]) * 256 * 256 * 256 + ord(self.buffer[-3]) * 256 * 256 + ord(self.buffer[-2]) * 256 + ord(self.buffer[-1])
                        if frame0 - self.frame < 10000 and frame0 - self.frame > 0 or self.frame == 0:
                            self.lock.acquire()
                            #print(self.buffer)
                            #print(self.len)
                            self.frame = frame0
                            self.array = np.frombuffer(self.buffer[0:-1], dtype=np.dtype('uint8'))
                            self.lock.release()
                        else:
                            self.errCount = self.errCount + 1
                    else:
                        self.errCount = self.errCount + 1
                else:
                    self.errCount = self.errCount + 1
            time.sleep(0.001)

recever1 = VideoReceiver(sock1)
recever1.start()
recever2 = VideoReceiver(sock2)
recever2.start()

def num2byte(num):
    return np.array([[num/256/256/256], [num/256/256], [num/256], [num]], dtype=uint8)

#cv2.namedWindow("Recever1")
#cv2.namedWindow("Recever2")
cv2.namedWindow("IMG")

currentFrame = 0
count1 = count2 = 0
time0 = time.time()
fps = 0

rospy.init_node('udp_image', anonymous = True)
bridge = CvBridge()
publisher = rospy.Publisher('image_topic', Image, queue_size=10)
publisherLeft = rospy.Publisher('camera/left/image_raw', Image, queue_size=10)
publisherRight = rospy.Publisher('camera/right/image_raw', Image, queue_size=10)
print("Correctly opened resource, starting to show feed.")

sendframe = 1
command_position_x, command_position_y, command_position_z  = 0, 0, 0
def callback_position(Point):
    global uav_position_x, uav_position_y, uav_position_z
    command_position_x = Point.x
    command_position_y = Point.y
    command_position_z = Point.z
    

def callback_tf(tf):
    global sendframe
    global command_position_x, command_position_y, command_position_z
    position_x = -tf.transforms[0].transform.translation.x
    position_y = -tf.transforms[0].transform.translation.y
    position_z = -tf.transforms[0].transform.translation.z
    qx = tf.transforms[0].transform.rotation.x
    qy = tf.transforms[0].transform.rotation.y
    qz = tf.transforms[0].transform.rotation.z
    qw = tf.transforms[0].transform.rotation.w

    # roll = atan2f(2.f * (qw*qz + qx*qy), 1-2*(qz*qz+qx*qx)); //Z
    # yaw =  asinf(2.f * (qw*qx - qy*qz)); //Y
    # pitch =atan2f(2.f * (qw*qy + qz*qx), 1-2*(qy*qy+qx*qx));//X

    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    pitch = math.asin(2 * (qw * qy - qz * qx))
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
 
   # print(position_x, position_y, position_z)
    magic = np.array([[153], [214], [52], [16]], dtype=uint8)
    buffer = np.concatenate((np.array([[ord('X')]], dtype=uint8), 
    num2byte((position_x+100)*10000), num2byte((position_y+100)*10000), num2byte((position_z+100)*10000),
    num2byte((roll+100)*10000), num2byte((pitch+100)*10000), num2byte((yaw+100)*10000),
    num2byte((command_position_x+100)*10000), num2byte((command_position_y+100)*10000), num2byte((command_position_z+100)*10000)
    ), axis=None) 
    buffer_sum = np.sum(buffer)
    buffer = np.concatenate(([buffer], np.array([[buffer_sum]], dtype=uint8)), axis=1)
    buffer = np.concatenate((magic, num2byte(sendframe), buffer.T, np.array([[ord('e')]], dtype=uint8), magic))#, [sum(buffer)]
    
    sendframe = sendframe + 1
    if buffer is not None:
        sockTrans1.sendto(buffer, server_address1)



rospy.Subscriber("uav_position",Point,callback_position)
rospy.Subscriber("tf", TFMessage, callback_tf)

while not rospy.is_shutdown() :
    time.sleep(0.001)
    array, frame = recever1.get_frame()
    newRecFrameFlag = False
    if frame > currentFrame:
        currentFrame = frame
        ####print('received from 1; Recfrom 1=',count1, ', Recfrom 2=',count2)
        img1 = cv2.imdecode(array, 1)
        img0 = img1
        count1 = count1 + 1
        newRecFrameFlag = True

    array, frame = recever2.get_frame()
    if frame > currentFrame:
        currentFrame = frame
        ####print('received from 2; Recfrom 1=',count1, ', Recfrom 2=',count2)
        img2 = cv2.imdecode(array, 1)
        img0 = img2
        count2 = count2 + 1
        newRecFrameFlag = True
    # cv2.imshow("Recever1", img1)
    # if cv2.waitKey(8) & 0xFF == ord('q'):
    #     break
    # cv2.imshow("Recever2", img2)
    # if cv2.waitKey(8) & 0xFF == ord('q'):
    #     break
    #print (count1,count2)
    if count1 > 0 and count2 > 0 and newRecFrameFlag:
        if img0.shape==(240, 640, 3) or img0.shape==(240*2, 640*2, 3):
            imageLeft = bridge.cv2_to_imgmsg(img0[:, 0:int(img0.shape[1]/2),:], encoding="bgr8")
            imageRight = bridge.cv2_to_imgmsg(img0[:, int(img0.shape[1]/2):,:], encoding="bgr8")
            try:
                publisherLeft.publish(imageLeft)
                publisherRight.publish(imageRight)
            except CvBridgeError as e:
                print(e)
        else:
            vtitch = np.hstack((img1, img2, img0))
            cv2.imshow("IMG", vtitch)
            image_message = bridge.cv2_to_imgmsg(img0, encoding="bgr8")
            try:
                publisher.publish(image_message)
            except CvBridgeError as e:
                print(e)
       # if cv2.waitKey(5) & 0xFF == ord('q'):
       #     break

    interval = (time.time() - time0)
    time0 = time.time()
    fps0 = 1/interval
    fps = 0.6 * fps + 0.4 * fps0
    

rospy.spin()
print("The client is quitting. If you wish to quite the server, simply call : \n")
#print("echo -n \"quit\" > /dev/udp/{}/{}".format(host, port))

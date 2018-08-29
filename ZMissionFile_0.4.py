import cv2
import numpy as np
#Flag = 0 means the initial statement
#Flag = 1 means the Window mission
#Flag = 2 means the Poles and Rope mission
#Flag = 3 means the QR code translation
#Flag = 4 means the Wind tunnel entry mission
#Flag = 5 means the Wind tunnel with hoops mission
#Flag = 6 means the landing mission
Flag_mission = 5

# This is for choose the centroid
# Record flags
# Flag = 0 means that this is the first time input
# Flag = 1 means that this is the normal condition and will be continue to find centroid
# Flag = 2 means that the centroid is correct and no need to change
# Flag = 3 means that the centroid maybe not correct and need to be fixed
# The initial value is 0
flag_centroid = 0
# The original centroid
centroid_origin_x = 0
centroid_origin_y = 0
# The new centroid input
centroid_nowaday_x = 0
centroid_nowaday_y = 0
# Record the extreme centorid data continuly
centroid_abnormal_x = []
centroid_abnormal_y = []
# Record the normal data intermittently
centroid_normal_x = []
centroid_normal_y = []
# Record the final result of centroid
centroid_final_x = 0
centroid_final_y = 0
# Distance threshold value
Maxdistance = 10
Truetime = 0
# UAV's position(the coordinate in the camera view)
center_x = 0
center_y = 0
# UAV's volume
# This is used for crash avoid, and the value here is the half of the whole body(I know it's 'width', but for same character...you know...obsession)
UAV_length = 0
UAV_height = 0
UAV_wideth = 0
# This is for transform the coordinate between the world and the camera(Try to read from slam)
worldcoordinate_x = 0
worldcoordinate_y = 0
worldcoordinate_h = 0
# Deviation permission
deviation_x = 0
deviation_y = 0

# this value is setted to break the test process
test_switch = 0

# these values are used for calculate centroid
x_weight_window = 0
y_weight_window = 0
weight_window = 0
x_weight_loop = 0
y_weight_loop = 0
weight_loop = 0
x_weight_rope = 0
y_weight_rope = 0
weight_rope = 0
centroid_x = 0
centroid_y = 0
# this function is used for calculate centroid
def Centroid_drawer(x_weight,y_weight,weight):
    if weight:
        centroid_x = int(x_weight/weight)
        centroid_y = int(y_weight/weight)
        cv2.circle(blur_1,(centroid_x,centroid_y), 10, (0,0,255), -1)
        return centroid_x,centroid_y
    else:return 0,0
# this function is used to calculate distance between two points
def distance( a_x , a_y , b_x , b_y ):
    distance = ((b_x - a_x)**2 + (b_y - a_y)**2)**0.5
    return distance
# Boundary values:
# Set the boundary value for the window background
window_bottom = np.array([20,100,20])
window_top = np.array([220,255,220])
# For Window mission
Max_area_window = 150000
Min_area_window = 50000

# For Pole and Rope mission
rope_bottom = np.array([20,100,20])
rope_top = np.array([220,255,220])
# For rope area
Max_area_rope = 20000
Min_area_rope = 10000
# For rope mission record
Flag_rope = 0
# For rope finding
# This is used for follow the line...

# This value shows the which square we come from
pre_index = 0
# Function to avoid poles
def avoid_poles():
    pass
# Function to follow line
def follow_line(img_thre, rope_areas, pre_index):
    # flag = 1 shows we are still following lines
    # flag = 2 shows we have already finished our trip
    # flag = 3 shows we met a pole and this interrupt with our route
    flag = 0
    # This is used for save the area of each square
    areas = []
    # This value records the max & min area
    min_area = 0
    max_area = 0
    # This value record which square has the max area
    node = 1
    # This value record how amny blocks have zero area
    zero = 0
    # Check if there are poles block us
    avoid_poles()
    # flag = 1 code starts here...
    if flag == 1:
        for rope_area in rope_areas:
            if rope_area[5] != pre_index:
                rope_img = img_thre[rope_area[1]:(rope_area[1]+rope_area[3]),rope_area[2]:rope_area+rope_area[4]]
                image, contours, hierarchy = cv2.findContours(rope_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
                area = 0
                for contour in contours:
                    if cv2.contourArea(contour) >= min_area:
                        if cv2.contourArea(contour) <= max_area:
                            area = area + cv2.contourArea(contour)
                areas.append(area)
        for area in areas:
            if area >= max_area:
                max_area = area
        for area in areas:
            if max_area != area:
                node = node + 1
        if node >= pre_index:
            node = node + 1
        pre_index = 8 - node
        # Check if we arrive the end of rope
        for i in range(0,6):
            if area[i] == 0:
                zero = zero + 1
        if zero == 7:
            flag = 2
        # Find the pre_index
        if node == 1: pre_index = 5
        elif node == 2: pre_index = 6
        elif node == 3: pre_index = 7
        elif node == 4: pre_index = 8
        elif node == 5: pre_index = 1
        elif node == 6: pre_index = 2
        elif node == 7: pre_index = 3
        elif node == 8: pre_index = 4
        if flag == 1: return 2,pre_index
    # Control code should starts here...
    
    # flag = 2 code starts here...
    elif flag == 2:
        return 3,pre_index
    # flag = 3 code starts here...
    elif flag == 3:
        return 2,pre_index
    else:
        return 2,pre_index
#[x,y,w,h,index]
# 0 represents the block at Middle
# 1 represents the block at E
# 2 represents the block at NE
# 3 represents the block at N
# 4 represents the block at NW
# 5 represents the block at W
# 6 represents the block at SW
# 7 represents the block at S
# 8 represents the block at SE
ROI_h = 0
ROI_w = 0
# X & Y points in the coordinate to cut the image
range_x_a = 0
range_x_b = 0
range_x_c = 0
range_x_d = 0
range_y_a = 0
range_y_b = 0
range_y_c = 0
range_y_d = 0
# ROI
rope_areas = [[range_x_b,range_y_b,ROI_w,ROI_h,1],
              [range_x_b,range_y_a,ROI_w,ROI_h,2],
              [range_x_c,range_y_a,ROI_w,ROI_h,3],
              [range_x_d,range_y_a,ROI_w,ROI_h,4],
              [range_x_d,range_y_b,ROI_w,ROI_h,5],
              [range_x_d,range_y_c,ROI_w,ROI_h,6],
              [range_x_c,range_y_c,ROI_w,ROI_h,7],
              [range_x_b,range_y_c,ROI_w,ROI_h,8]]

# For QR code translation mission


# For Wind tunnel entry mission
# Set the boundary value for the divider
divider_bottom = np.array([20,100,20])
divider_top = np.array([20,100,20])
# For divider area
Max_area_divider = 20000
Min_area_divider = 10000

# For wind tunnel with hoops mission
loop_bottom = np.array([20,100,20])
loop_top = np.array([220,225,220])
# For loop area
Max_area_loop = 10000
Min_area_loop = 500

# For landing mission

# Open Cameras:
# Camera1 is the one in the front:
camera1 = cv2.VideoCapture(0)
# Camera2 is the one at below:
'''camera2 = cv2.VideoCapture(0)'''

# Set Camera's size:
'''camera1.set(3,640)
camera1.set(4,480)
camera2.set(3,640)
camera2.set(4,480)'''

while(1):
    # read pictures from cameras
    ret_1, frame_1 = camera1.read()
    '''ret_2, frame_2 = camera2.read()'''
    
    # Self_Check code starts here...
    '''
        if camera1.isOpened():
            if camera2.isOpened():
                Flag_mission = 1
            else: print("Failed to open Camera2")
        else: print("Failed to open Camera1")
    '''
    
    # Test code->read the picture at the Desktop
    '''frame_1 = cv2.imread('/Users/Xavier/Desktop/1.png')'''
    
    # Data Re-Initial
    
    x_weight_window = 0
    y_weight_window = 0
    weight_window = 0
    x_weight_loop = 0
    y_weight_loop = 0
    weight_loop = 0
    # Window code starts here...
    if Flag_mission == 1:
        
        break
        '''
        # BGR Transform to HSV
        blur_1 = cv2.GaussianBlur(frame_1,(5,5),0)
        hsv_1 = cv2.cvtColor(blur_1,cv2.COLOR_BGR2HSV)
    
        # Build the mask for the window
        mask_window = cv2.inRange(hsv_1,window_bottom,window_top)
    
        # Bitwise operation
        res_window = cv2.bitwise_and(frame_1,frame_1,mask = mask_window)
        blur_window = cv2.GaussianBlur(res_window,(5,5),0)
        # BGR to GRAY
        gray_window = cv2.cvtColor(blur_window, cv2.COLOR_BGR2GRAY)
        # Threshold
        ret,thresh_window=cv2.threshold(gray_window,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # Find Contours
        image, contours_window, hierarchy = cv2.findContours(thresh_window,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

        for contour_window in contours_window:
            epsilon = 0.1*cv2.arcLength(contour_window,True)
            approx = cv2.approxPolyDP(contour_window,epsilon,True)
            if cv2.contourArea(contour_window) >= Min_area_window :
                if cv2.contourArea(contour_window) <= Max_area_window :
                    cv2.drawContours(blur_1, contour_window, -1, (255,0,0), 3)
                    M = cv2.moments(contour_window)
                    x_weight_window = x_weight_window + int(M['m10'])
                    y_weight_window = y_weight_window + int(M['m01'])
                    weight_window = weight_window + int(M['m00'])
        # Draw centroid
        if x_weight_window:
            if y_weight_window:
                centroid_x,centroid_y = Centroid_drawer(x_weight_window,y_weight_window,weight_window)
        print(centroid_x)
      
        if Truetime >= 5 and centroid_x:
            # length of normal/abnormal array
            length_normal = len(centroid_normal_x)
            length_abnormal = len(centroid_abnormal_x)
            print(flag_centroid)
            print(length_abnormal)
            # Judgement
            if flag_centroid == 0:
                flag_centroid = 1
                centroid_origin_x = centroid_x
                centroid_origin_y = centroid_y
            elif flag_centroid == 1:
                centroid_nowaday_x = centroid_x
                centroid_nowaday_y = centroid_y
                if distance(centroid_origin_x, centroid_origin_y, centroid_nowaday_x, centroid_nowaday_y) < Maxdistance:
                    centroid_normal_x.append(centroid_nowaday_x)
                    centroid_normal_y.append(centroid_nowaday_y)
                else :
                    centroid_abnormal_x.append(centroid_nowaday_x)
                    centroid_abnormal_y.append(centroid_nowaday_y)
                if length_abnormal <= 2 and length_normal == 10:
                    flag_centroid = 2
                    centroid_final_x = int(sum(centroid_normal_x)/(length_normal+1))
                    centroid_final_y = int(sum(centroid_normal_y)/(length_normal+1))
                elif length_abnormal >= 10 and length_normal <= 2:
                    flag_centroid = 0
                elif length_abnormal >=10 and length_normal >= 10:
                    flag_centroid = 3
                else:
                    flag_centroid = 0
            # Job done, return value
            elif flag_centroid == 2:
                cv2.circle(blur_1,(centroid_final_x,centroid_final_y), 10, (0,255,0), -1)
            # I think the most excetutable method is move the plane
            elif flag_centroid == 3:
                flag_centroid = 0
                del centroid_abnormal_x[:]
                del centroid_abnormal_y[:]
                del centroid_normal_x[:]
                del centroid_normal_y[:]
                
        # Image show (For test)
        cv2.imshow('Window',blur_1)
        cv2.imshow('Window Threshold',thresh_window)
        # Time recorder
        Truetime = Truetime + 1
        if cv2.waitKey(1) & 0xFF == ord('q'): test_switch = 1
        if test_switch: cv2.destroyAllWindows()
    '''
    # Mission Checkpoint 1
    
    # Poles and Rope code starts here...
    if Flag_mission == 2:
        '''
        # Gaussian
        blur_rope = cv2.GaussianBlur(frame_2,(5,5),0)
        # BGR Transform to HSV
        hsv_2 = cv2.cvtColor(blur_rope,cv2.COLOR_BGR2HSV)
        # Build the mask for the rope
        mask_rope = cv2.inRange(hsv_2,rope_bottom,rope_top)
        # Bitwise operation
        res_rope = cv2.bitwise_and(frame_2,frame_2,mask = mask_rope)
        blur_rope = cv2.GaussianBlur(res_rope,(5,5),0)
        # BGR to GRAY
        gray_rope = cv2.cvtColor(blur_rope, cv2.COLOR_BGR2GRAY)
        # Threshold
        ret,thresh_rope = cv2.threshold(gray_rope,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # Rope part 1(Find the rope and fly on it):
        if Flag_rope == 0:
            # Find Contours
            image, contours_rope, hierarchy = cv2.findContours(thresh_rope,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
            for contour_rope in contours_rope:
                epsilon = 0.1*cv2.arcLength(contour_rope,True)
                approx = cv2.approxPolyDP(contour_rope,epsilon,True)
                if cv2.contourArea(contour_rope) >= Min_area_rope :
                    if cv2.contourArea(contour_rope) <= Max_area_rope :
                        cv2.drawContours(blur, contour_rope, -1, (255,0,0), 3)
                        M = cv2.moments(contour_rope)
                        x_weight_rope = x_weight_rope + int(M['m10'])
                        y_weight_rope = y_weight_rope + int(M['m01'])
                        weight_rope = weight_rope + int(M['m00'])
            # Draw centroid
            centroid_x,centroid_y = Centroid_drawer(x_weight_rope,y_weight_rope,weight_rope)
            # Locate the pre_index
            if centroid_x in range(range_x_a,range_x_b):
                # this means we start at area No.2
                if centroid_y in range(range_y_a,range_y_b):
                    pre_index = 6
                    Flag_rope = 1
                # this means we start at area No.1
                elif centroid_y in range(range_y_b,range_y_c):
                    pre_index = 5
                    Flag_rope = 1
                # this means we start at area No.8
                elif centroid_y in range(range_y_c,range_y_d):
                    pre_index = 4
                    Flag_rope = 1
            elif centroid_x in range(range_x_b,range_x_c):
                # this means we start at area No.3
                if centroid_y in range(range_y_a,range_y_b):
                    pre_index = 7
                    Flag_rope = 1
                # this means we start at area No.7
                elif centroid_y in range(range_y_c,range_y_d):
                    pre_index = 3
                    Flag_rope = 1
            elif centroid_x in range(range_x_c,range_x_d):
                # this means we start at area No.4
                if centroid_y in range(range_y_a,range_y_b):
                    pre_index = 8
                    Flag_rope = 1
                # this means we start at area No.5
                elif centroid_y in range(range_y_b,range_y_c):
                    pre_index = 1
                    Flag_rope = 1
                # this means we start at area No.6
                elif centroid_y in range(range_y_c,range_y_d):
                    pre_index = 2
                    Flag_rope = 1

            
            if centroid_x <= center_x + deviation_x:
                if centroid_x >= center_x - deviation_x:
                    if centroid_y <= center_y + deviation_y:
                        if centroid_y >= center_y - deviation_y:
                            Flag_rope = 1
                
        # Rope part 2(Follow the rope)
        if Flag_rope == 1:
            Flag_mission,pre_index = follow_line(thresh_rope,rope_areas,pre_index)
            cv2.rectangle(blur_rope,(rope_areas[pre_index][1],rope_areas[pre_index][2]),(rope_areas[pre_index][1]+rope_areas[pre_index][3],rope_areas[pre_index][2]+rope_areas[pre_index][4]),(255,10,10),3)
            #Poles part:
        # Image show (For test)
        cv2.imshow('Rope',blur_rope)
        print(pre_index)
        if cv2.waitKey(1) & 0xFF == ord('q'): test_switch = 1
        if test_switch:
            cv2.destroyAllWindows()
        '''
        break
    # Mission Checkpoint 2
    
    # QR code translation code starts here...
    if Flag_mission == 3:
        '''
        #
        '''
        break
    # Mission Checkpoint 3
    
    # Wind tunnel code starts here...
    if Flag_mission == 4:
        '''
        # Code here...
        '''
        break
    # Mission Checkpoint 4
    
    # Wind tuunel with loops code starts here...
    if Flag_mission == 5:
        '''
        break
        '''
        # Delete when run the whole programme
        blur_1 = cv2.GaussianBlur(frame_1,(5,5),0)
        hsv_1 = cv2.cvtColor(blur_1,cv2.COLOR_BGR2HSV)
        # Build the mask for the loop
        mask_loop = cv2.inRange(hsv_1,loop_bottom,loop_top)
        
        # Bitwise operation
        res_loop = cv2.bitwise_and(frame_1,frame_1,mask = mask_loop)
        blur_loop = cv2.GaussianBlur(res_loop,(5,5),0)
        # BGR to GRAY
        gray_loop = cv2.cvtColor(blur_loop, cv2.COLOR_BGR2GRAY)
        # Threshold
        ret,thresh_loop = cv2.threshold(gray_loop,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # Find Contours
        image, contours_loop, hierarchy = cv2.findContours(thresh_loop,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        for contour_loop in contours_loop:
            epsilon = 0.1*cv2.arcLength(contour_loop,True)
            approx = cv2.approxPolyDP(contour_loop,epsilon,True)
            if cv2.contourArea(contour_loop) >= Min_area_loop :
                if cv2.contourArea(contour_loop) <= Max_area_loop :
                    cv2.drawContours(blur_loop, contour_loop, -1, (255,0,0), 3)
                    M = cv2.moments(contour_loop)
                    x_weight_loop = x_weight_loop + int(M['m10'])
                    y_weight_loop = y_weight_loop + int(M['m01'])
                    weight_loop = weight_loop + int(M['m00'])
        # Draw centroid
        if x_weight_loop:
            if y_weight_loop:
                centroid_x,centroid_y = Centroid_drawer(x_weight_loop,y_weight_loop,weight_loop)
    
        if Truetime >= 5 and centroid_x:
            # length of normal/abnormal array
            length_normal = len(centroid_normal_x)
            length_abnormal = len(centroid_abnormal_x)
            print(flag_centroid)
            print(length_abnormal)
            # Judgement
            if flag_centroid == 0:
                flag_centroid = 1
                centroid_origin_x = centroid_x
                centroid_origin_y = centroid_y
                del centroid_abnormal_x[:]
                del centroid_abnormal_y[:]
                del centroid_normal_x[:]
                del centroid_normal_y[:]
            elif flag_centroid == 1:
                centroid_nowaday_x = centroid_x
                centroid_nowaday_y = centroid_y
                if distance(centroid_origin_x, centroid_origin_y, centroid_nowaday_x, centroid_nowaday_y) < Maxdistance:
                    centroid_normal_x.append(centroid_nowaday_x)
                    centroid_normal_y.append(centroid_nowaday_y)
                else :
                    centroid_abnormal_x.append(centroid_nowaday_x)
                    centroid_abnormal_y.append(centroid_nowaday_y)
                if length_abnormal <= 2 and length_normal == 10:
                    flag_centroid = 2
                    centroid_final_x = int(sum(centroid_normal_x)/(length_normal+1))
                    centroid_final_y = int(sum(centroid_normal_y)/(length_normal+1))
                elif length_abnormal >= 10 and length_normal <= 2:
                    flag_centroid = 0
                elif length_abnormal >=10 and length_normal >= 10:
                    flag_centroid = 3
                else:
                    flag_centroid = 0
        # Job done, return value
            elif flag_centroid == 2:
                    cv2.circle(blur_1,(centroid_final_x,centroid_final_y), 10, (0,255,0), -1)
            # I think the most excetutable method is move the plane
            elif flag_centroid == 3:
                flag_centroid = 0
                del centroid_abnormal_x[:]
                del centroid_abnormal_y[:]
                del centroid_normal_x[:]
                del centroid_normal_y[:]

        Truetime = Truetime + 1
        # Image show (For test)
        cv2.imshow('Loop',blur_1)
        cv2.imshow('Loop Threshold',thresh_loop)
        if cv2.waitKey(1) & 0xFF == ord('q'): test_switch = 1
        if test_switch: cv2.destroyAllWindows()
        
    # Mission Checkpoint 5
    
    # Landing code starts here...
    if Flag_mission == 6:
        '''
        #
        '''
        break
    # Mission Checkpoint 6







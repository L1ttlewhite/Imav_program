import rospy
from nav_msgs.msg import Odometry
import tf
import time
odom = Odometry()

rospy.init_node('odom_pub', anonymous=True)
odom_pub = rospy.Publisher('odom',Odometry,queue_size=10)
listener = tf.TransformListener()

def Publish_odom_message():
    try:
        (transform, rotation) = listener.lookupTransform('/camera_pose',
                            '/camera_link', rospy.Time(0))
        odom.pose.pose.position.x = transform[0]
        odom.pose.pose.position.y = transform[1]
        odom.pose.pose.position.z = transform[2]
        odom.header.stamp = rospy.Time.now()
        odom_pub.publish(odom)
    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        print ('error')
    


rate = rospy.Rate(30)
while not rospy.is_shutdown():
    Publish_odom_message()
    rate.sleep()
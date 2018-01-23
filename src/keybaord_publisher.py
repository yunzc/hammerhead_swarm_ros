#!/usr/bin/env python
import rospy
from hammerhead_swarm_ros.msg import multi_bot, bot
from geometry_msgs.msg import Twist

rospy.init_node('cmd_publihser')
pub = rospy.Publisher('multi_bot_cmd', multi_bot, queue_size=10)

def callback(msg):
    # for now there are only one robot 
    pub_msg = multi_bot()
    b = bot()
    b.name = '1'
    b.cmd = msg 
    pub_msg.bots.append(b)
    pub.publish(pub_msg)

listner = rospy.Subscriber('cmd_vel', Twist, callback)

rospy.spin()
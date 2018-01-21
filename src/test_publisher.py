#!/usr/bin/env python
import rospy
from hammerhead_swarm_ros.msg import multi_bot, bot

def talker():
    pub = rospy.Publisher('multi_bot_cmd', multi_bot, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        msg = multi_bot()
        b = bot()
        b.name = '1'
        b.cmd.linear.x = 1; b.cmd.linear.y = 0; b.cmd.linear.z = 0
        b.cmd.angular.x = 0; b.cmd.angular.y = 0; b.cmd.angular.z = 1
        msg.bots.append(b)
        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
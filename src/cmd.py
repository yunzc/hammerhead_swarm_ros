#!/usr/bin/python

import roslib 
import rospy
from hammerhead_swarm_ros.msg import multi_bot
from std_msgs.msg import String 
from rospy.numpy_msg import numpy_msg
import numpy as np
import socket
import select
import sys
from thread import * # for python 3 it is _thread
import time

# goal is to store status_data and cmd_data for multiple robots 
# update ros topic and also listen 
# and then send to each individual robot 

number_of_robots = 1

IP_address = ''
Port = 1024 

cmd_data = {} # store next command to given to the corresponding robot
stat_data = {} # store any status feedback from the corresponding robot 
robot_conn = {} # stores robot name to corresponidng connection (socket)
# cmd_data: {robot=cmd}, stat_data: {robot=state}. robot_conn: {conn=robot}
# robot is like a serial number, or robot name 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP_address, Port))

server.listen(100)

def client_thread(conn, addr):
	while conn not in robot_conn:
		try: 
			message = conn.recv(2048)#.decode('utf-8') # might need .decode for python3
			if message: 
				robot = message # first message should be the robots name
				robot_conn[conn] = robot
				stat_data[robot] = ''
				cmd_data[robot] = ''
			else:
				print("connection failed")
				return 
		except:
			continue
	message = "Connected to server"
	conn.send(message.encode('utf-8'))
	while True:
		try: 
			message = conn.recv(2048).decode('utf-8')
			if message: 
				robot = robot_conn[conn]
				stat_data[robot] = message # message stored in stat_data
		except:
			continue


def remove(connection):
	robot = robot_conn[connection]
	del cmd_data[robot]
	del stat_data[robot]
	print("%s disconnected" %robot)
	del robot_conn[connection]
	return True 

def broadcast(): # boradcast message
	for conn in robot_conn:
		robot = robot_conn[conn]
		message = cmd_data[robot]
		try: 
			conn.send(message.encode('utf-8'))
		except: 
			conn.close()
			remove(conn)

rospy.init_node('command_center')
pub = rospy.Publisher('multi_bot_stat', String, queue_size=10)

def callback(msg):
	for i in range(number_of_robots):
		bot_data = msg.bots[i]
		bot_name = bot_data.name
		bot_cmd = bot_data.cmd
		bot_speed = np.sqrt(bot_cmd.linear.x**2 + bot_cmd.linear.y**2)
		bot_angv = bot_cmd.angular.z
		# store command 
		try:
			cmd_data[bot_name] = '%s %s' %(bot_speed, bot_angv)
		except:
			print("%s not connected" %bot_name)
			continue
	broadcast() 
	pub.publish(stat_data['1'])

while len(robot_conn) < number_of_robots:
	conn, addr = server.accept() # accep new connections 
	print('new connection')
	start_new_thread(client_thread, (conn, addr))
	print(robot_conn) 
	time.sleep(1)

sub = rospy.Subscriber('multi_bot_cmd', multi_bot, callback)
rospy.spin()

server.close() 
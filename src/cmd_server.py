#!/usr/bin/python

# Listens to ros cmd_vel messages and broadcasts to the individual bots 
# Author: Yun Chang 

import rospy
from geometry_msgs.msg import Twist
import numpy as np
import socket
import select
import sys
from thread import * # for python 3 it is _thread

class cmd_server(object):
	# server object for incoming clients 
	def __init__(self, IP_address='', Port=1024):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((IP_address, Port))
		self.server.listen(100)
		self.client_list = {} # dictionary to store client based on name 
		self.data = {} # client: (speed, angv)

	def callback(self, msg):
		# 2D 
		speed = np.sqrt(msg.linear.x**2 + msg.linear.y**2)
		angv = msg.angular.z
		# as of yet has not yet figured out the multivehicle control -- probably have to use
		# two cmd_vel publishers, for now assume publish to vehicle 2 always 
		self.data['2'] = (speed, angv)
		rospy.loginfo(self.data) 
		rospy.loginfo(self.client_list)

	def cmd_listener(self):
		rospy.init_node('cmd_vel_listener')
		rospy.Subscriber("/cmd_vel", Twist, self.callback)
		# rospy.spin()

	def client_thread(self, conn, addr):
		while conn not in self.client_list.values():
			try: 
				message = conn.recv(2048)#.decode('utf-8') # might need .decode for python3
				if message: 
					self.client_list[message] = conn
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
					print("<" + addr[0] + "> " + message)
				else:
					# message has no content if connection broken 
					self.remove(conn)
			except:
				continue

	def remove(self, conn):
		if conn in self.client_list:
			self.client_list.remove(conn)

	def broadcast(self):
		while True:
			for client in self.client_list:
				conn = self.client_list[client]
				try:
					message = self.data[client]
					conn.send(message.encode('utf-8'))
				except:
					conn.close()
					self.remove(conn)

	def run(self):
		start_new_thread(self.broadcast, ())
		while True:
			self.cmd_listener()
			conn, addr = self.server.accept() # accept connection requests 
			print(addr[0] + " connected")
			start_new_thread(self.client_thread, (conn, addr))
		conn.close()
		server.close()


if __name__ == '__main__':
	s = cmd_server()
	s.run()
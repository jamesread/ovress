#!/usr/bin/python

import amqp

class MessageHello(amqp.Message):
	def __init__(self):
		self(body = "hello")

class Manager:
	def __init__(self):
		print "AMQP init"
		self.connection = amqp.Connection(host = "localhost", userid = "guest", password = "guest");

		self.channel = amqp.Channel(self.connection)

		self.channel.close()
		self.connection.close()

	def sendHello(self):
		self.channel.basic_publish(MessageHello())

	def sayHello(self):
		print "Hello there!";

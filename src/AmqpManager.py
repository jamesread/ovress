#!/usr/bin/python

import json
import amqp
from socket import gethostname

class BaseMessage(object):
	def __init__(self, command = "base"):	
		self.command = command

	def toJson(self):
		return json.dumps(dict(self.__dict__.items() + {"command": self.command}.items()), indent = 4)

	def __repr__(self):
		return self.toJson()

class MessageHello(BaseMessage):
	def __init__(self):
		super(MessageHello, self).__init__("hello")

class MessageGoodbye(BaseMessage):
	def __init__(self):
		super(MessageGoodbye, self).__init__("goodbye")

class MessagePing(BaseMessage):
	def __init__(self):
		super(MessagePing, self).__init__("ping")

class MessagePong(BaseMessage):
	def __init__(self):
		super(MessagePong, self).__init__("pong")

		self.name = gethostname()

class MessageFileStatRequest(BaseMessage):
	def __init__(self, filename):
		super(MessageFileStatRequest, self).__init__("fileStatRequest")

		self.filename = filename
		self.checksum = "asdf"

class MessageFileStatResponse(BaseMessage):
	def __init__(self, filename):
		super(MessageFileStatResponse, self).__init__("fileStatResponse")

		self.filename = filename
		self.existsAt = [ "/foo", "/bar" ]
		self.checksum = "asdf"

class Manager:
	def __init__(self):
		print "AMQP init"
		self.connection = amqp.Connection(host = "localhost", userid = "guest", password = "guest");

		self.channel = amqp.Channel(self.connection)

		result = self.channel.queue_declare(exclusive = True)
		self.callbackQueue = result.queue

		self.channel.basic_consume(callback = self.onResponse, queue = self.callbackQueue)
		self.channel.basic_consume(callback = self.onRequest, queue = "rpc")
		self.channel.wait()
		print "Consumer configured"

	def onRequest(self, message):
		print "request", message

		self.channel.basic_ask(message);

	def onResponse(self, thing):
		print "response", thing

	def sendHello(self):
		self.send(MessageHello())

	def send(self, body):
		if type(body) == str:
			message = amqp.Message(body = body)
		else:
			message = amqp.Message(body = body.toJson())
			message.reply_to = self.callbackQueue

		self.channel.basic_publish(message, exchange = "ovress")

	def stop(self):
		self.channel.close()
		self.connection.close()

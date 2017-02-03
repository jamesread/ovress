#!/usr/bin/python

import simplejson as json
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingConnection as Connection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.channel import Channel
from socket import gethostname
from uuid import uuid1 as uuid
from threading import Thread

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
		self.connParams = ConnectionParameters(host = "localhost", credentials = PlainCredentials("guest", "guest"));

		self.connectionInit = Connection(parameters = self.connParams)
		self.connectionInit.channel().exchange_declare(exchange = "ovress", type = "fanout", durable = True, auto_delete = False)
		self.connectionInit.close();

		self.setupRequestQueue();
		self.setupResponseQueue();

	def setupRequestQueue(self):
		self.connectionRequests = Connection(parameters = self.connParams);
		self.channelRequests = self.connectionRequests.channel();

		self.requestQueue = str("requests-" + str(uuid()))
		self.channelRequests.queue_declare(queue = self.requestQueue, exclusive = True, auto_delete = True, durable = False)
		self.channelRequests.queue_bind(queue = self.requestQueue, exchange = "ovress", routing_key = "*")

		Thread(target = self.startConsumeRequests, name = "amqpReqQ").start()

	def startConsumeRequests(self):
		self.channelRequests.basic_consume(self.onRequest, queue = self.requestQueue)
		self.channelRequests.start_consuming()
		print "stopping requests"

	def setupResponseQueue(self):
		self.connectionResponses = Connection(parameters = self.connParams);
		self.channelResponses = self.connectionResponses.channel();

		self.responseQueue = str('responses-' + str(uuid()))
		self.channelResponses.queue_declare(exclusive = True, queue = self.responseQueue, auto_delete = True, durable = False)
		
		Thread(target = self.startConsumeResponses, name = "amqpRespQ").start();

	def startConsumeResponses(self):
		self.channelResponses.basic_consume(self.onResponse, queue = self.responseQueue)
		self.channelResponses.start_consuming()
		print "stopping responses"


	def onRequest(self, channel, delivery, properties, body):
		print "request", body

		self.channelRequests.basic_ack(delivery.delivery_tag);

	def onResponse(self, channel, delivery, properties, body):
		print "response", body

		self.channelRequests.basic_ack(delivery.delivery_tag);

	def sendHello(self):
		self.send(MessageHello())

	def send(self, baseMessage):
		properties = BasicProperties(reply_to = self.responseQueue)

		self.channelRequests.basic_publish("ovress", "route-all-the-things", baseMessage.toJson(), properties = properties)

	def stop(self):
		self.channelRequests.close()
		self.connectionRequests.close()

		self.channelResponses.close()
		self.connectionResponses.close()

#!/usr/bin/python

import cherrypy
from cherrypy import _cperror
import json
import argparse
from RootManager import RootManager
from Root import Root
from sys import exc_info
import os

JSON_OK = { "message": "ok"}

parser = argparse.ArgumentParser();
parser.add_argument('--port', default = 9010, type = int)
parser.add_argument('--bind-address', default = '0.0.0.0')
parser.add_argument('--session-timeout', default = 20160)
parser.add_argument('--foreground', action = 'store_true')
args = parser.parse_args();

class Api:
	def __init__(self):
		self.rootManager = RootManager();

		cherrypy.engine.subscribe("stop", self.onStop)

	def onStop(self):
		print "onstop"

		for root in self.rootManager.roots:
			print "no longer watching root:", root.path
			root.stop()

		print "stop callback complete!"

	@cherrypy.expose
	def default(self, *args, **kwargs):
		return "ovress"

	@cherrypy.expose
	def registerRoot(self, *path, **args):
		path = args['path']

		if os.path.exists(path):
			r1 = Root(path)

			self.rootManager.roots.append(r1)
			return self.outputJson(JSON_OK)
		else:
			self.outputJson(404, "path does not exist", "path-nonexistant")

	def outputJsonError(self, code, msg, uniqueType = ""):
		cherrypy.response.status = code;

		return self.outputJson({
			"type": "Error",
			"uniqueType": uniqueType,
			"message": msg
		})

	@cherrypy.expose
	def listRoots(self):
		return self.outputJson(self.rootManager.getRoots())

	def outputJson(self, structure, download=False, downloadFilename = "output.json"):
		if download:
			cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="' + downloadFilename + '" '
			
		cherrypy.response.headers['Content-Type'] = 'application/json'

		return json.dumps(structure);

def http_error_handler(status, message, traceback, version):
	return json.dumps({
		"httpStatus": status, 
		"type": "httpError",
		"message": message
	});


def error_handler():
	cherrypy.response.status = 500;
	cherrypy.response.headers['Content-Type'] = 'text/plain'

	exceptionInfo = exc_info()
	excType = exceptionInfo[0]
	exception = exceptionInfo[1]

	cherrypy.response.body = "\nUnhandled exception.\n" + "Message: " + exception.message + "\n" + "Type: " + str(excType.__name__)

	print exceptionInfo
		
api = Api();

cherrypy.config.update({
	'server.socket_host': args.bind_address,
	'server.socket_port': args.port,
	'tools.sessions.on': True,
	'tools.sessions.storage_type': 'ram',
	'tools.sessions.timeout': args.session_timeout,
	'request.error_response': error_handler,
	'request.error_page': {'default': http_error_handler }
})

if not args.foreground:
	cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

cherrypy.quickstart(api);

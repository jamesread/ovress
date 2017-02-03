#!/usr/bin/python

import threadNamePatch

import cherrypy
from cherrypy import _cperror
import simplejson as json
from sys import exc_info
import os
import os.path
from Config import Config
from Api import Api

import argparse
parser = argparse.ArgumentParser();
parser.add_argument('--port', default = 9010, type = int)
parser.add_argument('--bind-address', default = '0.0.0.0')
parser.add_argument('--session-timeout', default = 20160)
parser.add_argument('-F', '--foreground', action = 'store_true')
args = parser.parse_args();

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
Config.instance = Config()
Config.instance.reloadUserConfig(api.rootManager)

uidir = os.path.realpath(os.path.dirname(__file__) + '/../ui/')
print uidir

cherrypy.config.update({
	'server.socket_host': args.bind_address,
	'server.socket_port': args.port,
	'tools.sessions.on': True,
	'tools.sessions.storage_type': 'ram',
	'tools.sessions.timeout': args.session_timeout,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': uidir,
	'request.error_response': error_handler,
	'request.error_page': {'default': http_error_handler }
})

if not args.foreground:
	cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

cherrypy.quickstart(api);

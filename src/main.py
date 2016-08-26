#!/usr/bin/python

import cherrypy
from cherrypy import _cperror
import json
import argparse
from RootManager import RootManager
from Root import Root
from sys import exc_info
import os
import os.path
import Config

JSON_OK = { "message": "ok"}

parser = argparse.ArgumentParser();
parser.add_argument('--port', default = 9010, type = int)
parser.add_argument('--bind-address', default = '0.0.0.0')
parser.add_argument('--session-timeout', default = 20160)
parser.add_argument('-F', '--foreground', action = 'store_true')
args = parser.parse_args();

class Api:
	def __init__(self):
                self.config = Config.Config()
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
		return '<h1>ovress</h1><script   src="https://code.jquery.com/jquery-3.1.0.min.js"   integrity="sha256-cCueBR6CsyA4/9szpPfrX3s49M9vUU5BgtiJj06wt/s="   crossorigin="anonymous"></script><script type = "text/javascript" src = "main.js"></script>'

	@cherrypy.expose
	def registerRoot(self, *path, **args):
		path = args['path']

		if os.path.exists(path):
			r1 = Root(path)

			self.rootManager.roots.append(r1)
			return self.outputJsonOk()
		else:
			return self.outputError(404, "path does not exist", "path-nonexistant")

        @cherrypy.expose
        def removeRoot(self, *path, **args):
                path = args['path']

                root = self.rootManager.find();

                if root == None:
                    return self.outputError(404, "path not found", "path-not-found")

                root.stop()
                
                self.rootManager.roots.remove(root)
                return self.outputJsonOk()


	@cherrypy.expose
	def listRoots(self):
                ret = [];
                
                for root in self.rootManager.getRoots():
                    ret.append({
                        "path": root.path
                    })

		return self.outputJson({
                    "type": "root-list",
                    "count": len(ret),
                    "roots": ret
                })

        @cherrypy.expose
        def listRootContents(self, *path, **args):
                if "path" not in args:
                    return self.outputErrorRequiredArg("path")

                path = args['path']

                root = self.rootManager.find(path)

                if root == None:
                    return self.outputError(404, "path not found", "path-not-found")

                return self.outputJson({
                    "type": "root-contents",
                    "path": root.path,
                    "contents": root.contents
                })

	@cherrypy.expose
        def resaveRoot(self, *path, **args):
                if "path" not in args:
                    return self.outputErrorRequiredArg("path")

                path = args['path']

                root = self.rootManager.find(path)

                if root == None:
                    return self.outputError(404, "path not found", "path-not-found")

                contentsFile = root.save()

                return self.outputJson({
                    "type": "save-result",
                    "contents": contentsFile
                })

        def outputError(self, errorCode, errorMessage, errorType):
		cherrypy.response.status = errorCode;

                return self.outputJson({
                    "code": errorCode,
                    "message": errorMessage,
                    "type": errorType
                })
            
        def outputErrorRequiredArg(self, arg):
                msg = "The argument '" + arg + "' is required"; 
                return self.outputError(404, msg, "required-arg")

	def outputJson(self, structure, download=False, downloadFilename = "output.json"):
		if download:
			cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="' + downloadFilename + '" '
			
		cherrypy.response.headers['Content-Type'] = 'application/json'

		return json.dumps(structure);

        def outputJsonOk(self):
                return self.outputJson(JSON_OK);

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

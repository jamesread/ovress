import simplejson as json
import cherrypy
from cherrypy import _cperror
from RootManager import RootManager
from Root import Root
import os.path
from Config import Config
import sys

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
    def exit(self, *args, **kwargs):
            if "confirm" in kwargs:
                sys.exit()

            return self.outputJson({
                "message": "You need to pass the 'confirm' argument to exit."
            })

    @cherrypy.expose
    def index(self):
        return '<h1>ovress</h1><script src="https://code.jquery.com/jquery-3.1.0.min.js"   integrity="sha256-cCueBR6CsyA4/9szpPfrX3s49M9vUU5BgtiJj06wt/s="   crossorigin="anonymous"></script><script type = "text/javascript" src = "main.js"></script><link rel = "stylesheet" type = "text/css" href = "style.css" />'

    @cherrypy.expose
    def default(self, *args, **kwargs):
                return self.outputError(404, "Resource not found.", "resource-not-found")

    @cherrypy.expose
    def status(self, *arg, **kwargs):
            return self.outputJson({
                "status": "ok",
                "rootCount": self.rootManager.count() 
            })

    @cherrypy.expose
    def rescan(self, *path, **args):
            path = args['path']

            root = self.rootManager.find(path)

            if root == None:
                return self.outputErrorPathNotFound()

            root.startRescan()

            return self.outputJsonOk()

    @cherrypy.expose
    def stopRescan(self, *path, **args):
        root = self.rootManager.find(args['path'])

        if root == None:
            return self.outputErrorPathNotFound()

        root.stop();

        return self.outputJsonOk()

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

            root = self.rootManager.find(path);

            if root == None:
                return self.outputErrorPathNotFound()

            root.stop()
            
            self.rootManager.roots.remove(root)
            return self.outputJsonOk()


    @cherrypy.expose
    def listRoots(self):
        ret = [];
        
        for root in self.rootManager.getRoots():
            ret.append({
                "path": root.path,
                "status": root.status,
                "peers": root.peers,
                "contents": root.contents
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
            return self.outputErrorPathNotFound()

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
                return self.outputErrorPathNotFound()

            contentsFile = root.save()

            return self.outputJson({
                "type": "save-result",
                "contents": contentsFile
            })


    def outputErrorPathNotFound(self):
        return self.outputError(404, "path not found", "path-not-found")

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

        return json.dumps(structure, for_json = True);

    def outputJsonOk(self):
        JSON_OK = { "message": "ok"}

        return self.outputJson(JSON_OK);



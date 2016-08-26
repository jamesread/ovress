#!/usr/bin/python

import os
import os.path
import json
import md5
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

class Root(ProcessEvent):
	def __init__(self, path):
		self.path = path;
		self.watchManager = WatchManager()

		self.watchMask = EventsCodes.ALL_FLAGS['IN_DELETE'] | EventsCodes.ALL_FLAGS['IN_CREATE']

		self.notifier = ThreadedNotifier(self.watchManager, default_proc_fun=self)
		self.notifier.start()

		self.wdd = self.watchManager.add_watch(path, self.watchMask, rec=True)
                
                self.contents = {}
                self.load()  

                self.rescan()
                self.save()

        def save(self):
                try:
                    handle = file(self.getContentsFilepath(), 'w+')
                    handle.write(json.dumps(self.contents, sort_keys=True, indent=4))
                    handle.close()
                except Exception as e:
                    print e

                return self.getContentsFilepath()

        def load(self):
                try: 
                    handle = file(self.getContentsFilepath(), 'r')
                    jsonRaw = handle.read()
                    jsonContents = json.loads(jsonRaw)

                    print jsonContents
                except Exception as e:
                    print "Load failed:" + str(e)
                    return

                self.contents = jsonContents

        def getContentsFilepath(self):
                contentsDir = os.path.join(os.path.join(self.path, ".ovress"))

                if not os.path.isdir(contentsDir):
                    os.mkdir(contentsDir)

                return os.path.join(contentsDir, "contents.json")

        def rescan(self):
                self.contents["/home/jread/one"] = self.getFileMetadata("/home/jread/one")
                self.contents["/home/jread/two"] = self.getFileMetadata("/home/jread/two")

        def getFileMetadata(self, path):
                exists = False;
                filesize = 0;
                filetype = '?';
                md5 = ""

                if os.path.exists(path):
                    exists = True
                    filesize = os.path.getsize(path)
                    md5 = md5.md5(path).hexdigest()

                return {
                    "exists": exists,
                    "filesize": filesize,
                    "type": filetype,
                    "md5": md5
                }

        def getContents(self):
                return self.contents

	def process_IN_CREATE(self, event):
                fullPath = os.path.join(event.path, event.name)

		print "Create %s" % fullPath

                self.contents[fullPath] = self.getFileMetadata(fullPath)

	def process_IN_DELETE(self, event):
                fullPath = os.path.join(event.path, event.name)

		print "Delete %s" % fullPath

                self.contents[fullPath] = self.getFileMetadata(fullPath)

	def stop(self):
		self.notifier.stop();

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

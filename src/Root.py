#!/usr/bin/python

import os
import os.path
import simplejson as json
import md5
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
from threading import Thread
from Peer import Peer
from time import time, sleep

class Root(ProcessEvent):
        scanThread = None
        continueScanning = True
        peers = []

	def __init__(self, path):
		self.path = path;
                self.setStatus("???")

                self.peers.append(Peer("dummy", self.path))
               
		self.watchManager = WatchManager()

		self.watchMask = EventsCodes.ALL_FLAGS['IN_DELETE'] | EventsCodes.ALL_FLAGS['IN_CREATE']

		self.notifier = ThreadedNotifier(self.watchManager, default_proc_fun=self)
		self.notifier.start()

		self.wdd = self.watchManager.add_watch(path, self.watchMask, rec=True)
                
                self.contents = {}
                self.load()  

                self.rescan()
                self.save()

        def setStatus(self, msg):
            print "root: " + self.path + " status: " + msg
            self.status = msg;

        def save(self):
                print "Saving to: ", self.getContentsFilepath()
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
                if self.scanThread == None or not self.scanThread.is_alive():
                    self.scanThread = Thread(target = self.doScan, name = "scanThread")
                    self.scanThread.start()

        def doScan(self):
                countNew = 0
                self.setStatus("scanning")

                for dirname, subdirs, fileList in os.walk(self.path):
                    for filename in fileList:
                        absolutePath = os.path.join(dirname, filename)
                        relativePath = absolutePath.replace(self.path, "")

                        generateMetadata = True

                        try: 
                            fileMetadata = self.contents[relativePath]
                            
                            if (fileMetadata['refreshed'] + 3600) > time():
                                self.setStatus("Using cached scan of: " + relativePath)
                                generateMetadata = False
                        except KeyError:
                                pass

                        if generateMetadata:
                            self.setStatus("Generating Metadata: " + absolutePath)

                            fileMetadata = self.getFileMetadata(absolutePath)
                            self.contents[relativePath] = fileMetadata

                            countNew = countNew + 1
                            sleep(0.5)

                        if countNew == config.saveInterval:
                            countNew = 0
                            self.save()

                        for peer in self.peers:
                                peer.onScanFile(relativePath, fileMetadata)

                        if not self.continueScanning: return

                self.setStatus("complete")

        def getFileMetadata(self, path):
                exists = False;
                filesize = 0;
                filetype = '?';
                md5sum = ""

                if os.path.exists(path):
                    exists = True
                    filesize = os.path.getsize(path)
                    md5sum = md5.md5(path).hexdigest()

                return {
                    "exists": exists,
                    "filesize": filesize,
                    "type": filetype,
                    "md5": md5sum,
                    "refreshed": time()
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
                self.continueScanning = False
		self.notifier.stop();

        def getPeers(self):
                return self.peers

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

#!/usr/bin/python

import os
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

class Root(ProcessEvent):
	def __init__(self, path):
		self.path = path;
		self.watchManager = WatchManager()

		self.watchMask = EventsCodes.ALL_FLAGS['IN_DELETE'] | EventsCodes.ALL_FLAGS['IN_CREATE']

		self.notifier = ThreadedNotifier(self.watchManager, default_proc_fun=self)
		self.notifier.start()

		self.wdd = self.watchManager.add_watch(path, self.watchMask, rec=True)

	def process_IN_CREATE(self, event):
		print "Create %s" % os.path.join(event.path, event.name)

	def process_IN_DELETE(self, event):
		print "Delete %s" % os.path.join(event.path, event.name)

	def stop(self):
		self.notifier.stop();

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

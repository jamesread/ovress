#!/usr/bin/python

class RootManager():
	def __init__(self):
		self.roots = []
	
	def getRoots(self):
		return self.roots

        def find(self, path):
            for root in self.roots:
                if root.path == path:
                    return root

            return None

        def count(self):
            return len(self.roots)


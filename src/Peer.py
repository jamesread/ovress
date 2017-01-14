from DiffList import DiffList

class Peer():
    id = "???"
    path = None
    diffs = DiffList()
    contents = {}

    def __init__(self, id, path):
        self.id = id
        self.path = path

    def onScanFile(self, relativePath, localMetadata):
        if relativePath in self.contents:
            remoteMetadata = self.contents[relativePath]

            if remoteFile["md5"] != localMetadata['md5']:
                self.diffs.checksumMismatch(relativePath)

            # remote and local are the same
        else:
            self.diffs.existsLocalOnly(relativePath)

    def for_json(self):
        return {
            "id": self.id,
            "diffs": self.diffs,
            "contents": self.contents
        }


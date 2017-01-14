class DiffList:
    diffs = {}

    def existsLocalOnly(self, filename):
        self.diffs[filename] = "LOCAL_ONLY"

    def checksumMismatch(self, filename):
        self.diffs[filename] = "MISMATCH"

    def existsRemoteOnly(self, filename):
        self.diffs[filename] = "REMOTE_ONLY"

    def for_json(self):
        return {
            "countLocalOnly": 0,
            "countMismatch": 0,
            "countRemoteOnly": 0,
            "diffs": self.diffs
        }

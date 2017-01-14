import ConfigParser
import os
from Root import Root

class Config:
    bindAddress = "0.0.0.0"
    rootManager = None
    saveInterval = 10

    def __init__(self, rootManager):
        self.configParser = ConfigParser.SafeConfigParser()

        self.rootManager = rootManager

        self.reloadUserConfig();

    def reloadUserConfig(self):
        homePath = os.path.join(os.getenv('HOME'), '.ovress.cfg')

        try: 
            res = self.configParser.readfp(open(homePath))
        except: 
            return

        for section in self.configParser.sections():
            print "section:", section

            if section == "server":
                self.bindAddress = self.configParser.get("server", "bind")
            else:
                if self.configParser.has_option(section, "path"):
                    path = self.configParser.get(section, "path")

                    self.rootManager.roots.append(Root(path))



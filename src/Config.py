import ConfigParser
import os

class Config:
    instance = None

    bindAddress = "0.0.0.0"
    saveInterval = 10

    def __init__(self):
        self.configParser = ConfigParser.SafeConfigParser()

    def __getattr__(self, name):
        return getattr(self.instance, name);

    def reloadUserConfig(self, rootManager):
        from Root import Root

        homePath = os.path.join(os.getenv('HOME'), '.ovress.cfg')

        try: 
            res = self.configParser.readfp(open(homePath))
        except Exception as e: 
            print "config fail", e
            return

        for section in self.configParser.sections():
            print "section:", section

            if section == "server":
                self.bindAddress = self.configParser.get("server", "bind")
            else:
                if self.configParser.has_option(section, "path"):
                    path = self.configParser.get(section, "path")

                    rootManager.roots.append(Root(path))



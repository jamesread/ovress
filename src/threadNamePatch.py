try: 
    import threading
    import prctl
    def set_thread_name(name): prctl.set_name(name)

    def _thread_name_hack(self):
        set_thread_name(self.name)
        threading.Thread.__bootstrap_original__(self)

    threading.Thread.__bootstrap_original__ = threading.Thread._Thread__bootstrap
    threading.Thread._Thread__bootstrap = _thread_name_hack
except ImportError:
    print('WARN: prctl module is not installed. You will not be able to see thread names')
    def set_thread_name(name): pass
except Exception:
    print "Exception"
    def set_thread_name(name): pass

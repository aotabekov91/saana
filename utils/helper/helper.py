import os

def appCommand(func):
    def inner(self, request):
        if self.check_window_class():
            cmd=func(self, request)
            if cmd: os.popen(cmd)
    return inner 

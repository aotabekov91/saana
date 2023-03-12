import os

def osAppCommand(func):
    def inner(self, request):
        if self.generic.check_window_class():
            cmd=func(self, request)
            if cmd: os.popen(cmd)
    return inner 

def osGenericCommand(func):
    def inner(self, request):
        cmd=func(self, request)
        if cmd: os.popen(cmd)
    return inner 

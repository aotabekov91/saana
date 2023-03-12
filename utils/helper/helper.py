import os

def osAppCommand(func):
    def inner(self, request):
        cwindow=self.get_current_window()
        if cwindow.window_class==self.window_class:
            cmd=func(self, request)
            if cmd: os.popen(cmd)
        else:
            self.checkAction({})
    return inner 

def osGenericCommand(func):
    def inner(self, request):
        cmd=func(self, request)
        if cmd: os.popen(cmd)
    return inner 

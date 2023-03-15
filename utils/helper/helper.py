import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def osAppCommand(func):
    def inner(self, request):
        cond1=self.window_classes=='all'
        window_class=self.get_current_window()
        cond2=window_class in self.window_classes
        print(cond1, cond2, window_class)
        if cond1 or cond2:
            repeat_func=getattr(self, 'repeat', None)
            if repeat_func:
                times=int(repeat_func(request))
            else:
                times=1
            cmd=func(self, request)
            if cmd:
                cmd=cmd.format(repeat=times)
                print(cmd, times)
                os.popen(cmd)
        else:
            self.checkAction({})
    return inner 

def osGenericCommand(func):
    def inner(self, request):
        cmd=func(self, request)
        repeat_func=getattr(self, 'repeat', None)
        if repeat_func:
            times=repeat_func(request)
        else:
            times=1
        if cmd:
            cmd=cmd.format(repeat=times)
            os.popen(cmd)
    return inner 

class ZMQListener(QObject):

    request = pyqtSignal(dict)

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent=parent
        self.running = True

    def loop(self):
        while self.running:
            request = self.parent.socket.recv_json()
            self.request.emit(request)


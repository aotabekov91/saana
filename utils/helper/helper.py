import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def repeat(func):
    def inner(self, request):
        cmd=func(self, request)
        slot_names=request['slot_names']
        times=slot_names.get('repeat', 1)
        cmd=cmd.format(repeat=times)
        print(cmd, slot_names)
        return cmd.format(repeat=times)
    return inner

def osAppCommand(func):
    def inner(self, request):
        cond1=self.window_classes=='all'
        window_class=self.get_current_window()
        cond2=window_class in self.window_classes
        if cond1 or cond2:
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


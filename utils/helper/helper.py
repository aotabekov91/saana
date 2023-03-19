import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        else:
            print(f'{cls.__name__} is already running')
        return cls._instance


def osAppCommand(checkActionOnFinish=False, checkWindowType=True):
    def _osAppCommand(func):
        def inner(self, request):
            cond=True
            if checkWindowType:
                cond1 = self.window_classes == 'all'
                window = self.get_current_window()
                cond2 = window.window_class in self.window_classes
                cond = cond1 or cond2
            if cond: 
                repeat_func = getattr(self, 'repeat', None)
                if repeat_func:
                    times = int(repeat_func(request))
                else:
                    times = 1
                cmd = func(self, request)
                if cmd:
                    cmd = cmd.format(repeat=times)
                    os.popen(cmd)
            if checkActionOnFinish:
                self.checkAction({})
        return inner
    return _osAppCommand


def osGenericCommand(func):
    def inner(self, request):
        cmd = func(self, request)
        repeat_func = getattr(self, 'repeat', None)
        if repeat_func:
            times = repeat_func(request)
        else:
            times = 1
        if cmd:
            cmd = cmd.format(repeat=times)
            os.popen(cmd)
    return inner


class ZMQListener(QObject):

    request = pyqtSignal(dict)

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent = parent
        self.running = True

    def loop(self):
        while self.running:
            request = self.parent.socket.recv_json()
            self.request.emit(request)

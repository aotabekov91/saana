import os
import asyncio

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def command(checkActionOnFinish=False, checkWindowType=True, windowCommand=False):
    def _command(func):
        def inner(self, request):
            cond=True
            if checkWindowType:
                if self.window_classes != 'all':
                    window = self.get_current_window()
                    cond = window.window_class in self.window_classes
            if cond: 
                repeat_func = getattr(self, 'repeat', None)
                if repeat_func:
                    times = int(repeat_func(request))
                else:
                    times = 1
                cmd = func(self, request)
                if cmd:
                    print(f'Running command: {cmd}')
                    cmd = cmd.format(repeat=times)
                    if windowCommand:
                        asyncio.run(self.manager.command(cmd))
                    else:
                        os.popen(cmd)
            if checkActionOnFinish:
                self.checkAction(request)
        return inner
    return _command

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

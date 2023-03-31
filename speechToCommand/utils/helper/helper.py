import os
import time
import asyncio

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def command(checkActionOnFinish=False, checkWindowType=True, 
            windowCommand=False, delayAction=None, waitAction=None):
    def _command(func):
        def inner(self, request={}, *args, **kwargs):
            cond=True
            if checkWindowType:
                if self.window_classes != 'all':
                    cond = self.get_window_class() in self.window_classes
            if delayAction: time.sleep(delayAction)
            if cond: 
                cmd = func(self, request, *args, **kwargs)
                if cmd:
                    if hasattr(self, 'parse_repeats'):
                        times = self.parse_repeats(request)
                        cmd = cmd.format(repeat=times)
                    print(f'Running command: {cmd}')
                    if windowCommand:
                        asyncio.run(self.manager.command(cmd))
                    else:
                        os.popen(cmd)
            if waitAction: time.sleep(waitAction)
            if checkActionOnFinish:
                if hasattr(self, 'checkAction'):
                    self.checkAction(request)
                elif hasattr(self, 'mode'):
                    self.mode.checkAction(request)
        return inner
    return _command

class ZMQListener(QObject):

    request = pyqtSignal(dict)

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent = parent

    def loop(self):
        while self.parent.running:
            request = self.parent.socket.recv_json()
            self.request.emit(request)

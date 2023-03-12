import os
import sys
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode

class QutebrowserMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(QutebrowserMode, self).__init__(
                 keyword='browser', 
                 info='Qutebrowser', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.window_class='qutebrowser'
        self.manager=asyncio.run(Connection().connect())


    def backwardAction(self, request={}):
        if self.check_window_class():
            os.popen('xdotool getactivewindow key shift+h')

    def forwardAction(self, request={}):
        if self.check_window_class():
            os.popen('xdotool getactivewindow key shift+l')

    def chooseAction(self, request):
        if self.check_window_class():
            slot_names=request.get('slot_names', {})
            text=slot_names.get('item', '')
            os.popen(f'xdotool getactivewindow type o " "{text}')

    def openTabAction(self, request):
        if self.check_window_class():
            slot_names=request.get('slot_names', {})
            text=slot_names.get('text', ' ')
            os.popen(f'xdotool getactivewindow type o -t " "{text}')

    def nextTabAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+j')

    def prevTabAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+k')

    def doneAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type d')

    def hintAction(self, request={}):
        if self.check_window_class():
            slot_names=request.get('slot_names', {})
            hint=slot_names.get('hint', None)
            if hint:
                hint=''.join([h[0] for h in hint.split(' ')])
            else:
                hint='f'
            os.popen(f'xdotool getactivewindow type {hint}')

    def zoomInAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type +')

    def zoomOutAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type -')

    def moveDownAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key ctrl+f') 

    def moveUpAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key ctrl+b') 

    def quickmarkAction(self, request={}):
        if self.check_window_class():
            slot_names=request.get('slot_names', {})
            mark=slot_names.get('mark', '')
            os.popen(f'xdotool getactivewindow type m {mark}') 

    def hintTabAction(self, request={}):
        if self.check_window_class():
            slot_names=request.get('slot_names', {})
            hint=slot_names.get('hint', None)
            if hint:
                hint=''.join([h[0] for h in hint.split(' ')])
            else:
                hint='F'
            os.popen(f'xdotool getactivewindow type {hint}')

if __name__=='__main__':
    app=QutebrowserMode(port=33333)
    app.run()

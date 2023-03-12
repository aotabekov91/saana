import os
import sys
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.helper import osAppCommand

class QutebrowserMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(QutebrowserMode, self).__init__(
                 keyword='browser', 
                 info='Qutebrowser', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.window_class='qutebrowser'

    @osAppCommand
    def backwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+h'

    @osAppCommand
    def forwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+l'

    @osAppCommand
    def chooseAction(self, request):
        slot_names=request.get('slot_names', {})
        text=slot_names.get('item', '')
        return f'xdotool getactivewindow type o " "{text}'

    @osAppCommand
    def openTabAction(self, request):
        slot_names=request.get('slot_names', {})
        text=slot_names.get('text', ' ')
        return f'xdotool getactivewindow type o -t " "{text}'

    @osAppCommand
    def moveLeftAction(self, request):
        return f'xdotool getactivewindow key shift+j'

    @osAppCommand
    def moveRightAction(self, request):
        return f'xdotool getactivewindow key shift+k'

    @osAppCommand
    def doneAction(self, request):
        return f'xdotool getactivewindow type d'

    @osAppCommand
    def hintAction(self, request={}):
        slot_names=request.get('slot_names', {})
        hint=slot_names.get('hint', None)
        if hint:
            hint=''.join([h[0] for h in hint.split(' ')])
        else:
            hint='f'
        return f'xdotool getactivewindow type {hint}'

    @osAppCommand
    def moveDownAction(self, request={}):
        return f'xdotool getactivewindow key ctrl+f'

    @osAppCommand
    def moveUpAction(self, request={}):
        return f'xdotool getactivewindow key ctrl+b'

    @osAppCommand
    def quickmarkAction(self, request={}):
        slot_names=request.get('slot_names', {})
        mark=slot_names.get('mark', '')
        return f'xdotool getactivewindow type m {mark}'

    @osAppCommand
    def hintTabAction(self, request={}):
        slot_names=request.get('slot_names', {})
        hint=slot_names.get('hint', None)
        if hint:
            hint=''.join([h[0] for h in hint.split(' ')])
        else:
            hint='F'
        return f'xdotool getactivewindow type {hint}'

if __name__=='__main__':
    app=QutebrowserMode(port=33333)
    app.run()

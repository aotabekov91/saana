import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import osAppCommand
from speechToCommand.utils.moder import BaseGenericMode

class VimMode(BaseGenericMode):
    def __init__(self,
                 keyword='vimmode', 
                 info='VimMode', 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 window_classes=['vim', 'ranger', 'kitty', 'tmux']):

        super(VimMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

    @osAppCommand()
    def refreshAction(self, request={}):
        return 'xdotool getactivewindow type r'

    @osAppCommand()
    def markSetAction(self, request={}):
        self.activateInput('setTextInitialsAction')
        return 'xdotool getactivewindow type m'

    @osAppCommand()
    def markJumpAction(self, request):
        self.activateInput('setTextInitialsAction')
        return f"xdotool getactivewindow type '`'"

    @osAppCommand()
    def hintJumpAction(self, request):
        self.activateInput('setTextInitialsAction')
        return 'xdotool getactivewindow type ..w'

    @osAppCommand()
    def moveDownAction(self, request):
        return 'xdotool getactivewindow type {repeat}j'

    @osAppCommand()
    def moveUpAction(self, request):
        return 'xdotool getactivewindow type {repeat}k'

    @osAppCommand()
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow type {repeat}h'

    @osAppCommand()
    def moveRightAction(self, request):
        return 'xdotool getactivewindow type {repeat}l'

    @osAppCommand()
    def forwardAction(self, request):
        return 'xdotool getactivewindow type {repeat}ctrl+f'

    @osAppCommand()
    def backwardAction(self, request):
        return 'xdotool getactivewindow type {repeat}ctrl+b'

    @osAppCommand()
    def gotoBeginAction(self, request={}):
        return 'xdotool getactivewindow key --repeat 2 g'

    @osAppCommand()
    def gotoEndAction(self, request={}):
        return 'xdotool getactivewindow type G'

if __name__=='__main__':
    app=VimMode(port=33333, parent_port=44444)
    app.run()

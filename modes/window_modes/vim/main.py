import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import osAppCommand
from speechToCommand.utils.window import BaseGenericMode

class VimMode(BaseGenericMode):
    def __init__(self,
                 keyword='vimmode', 
                 info='VimMode', 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 window_classes=['vim', 'ranger']):

        super(VimMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

    @osAppCommand
    def showHintAction(self, request):
        raise

    @osAppCommand
    def followHintAction(self, request):
        raise

    @osAppCommand
    def createHintAction(self, request):
        raise

    @osAppCommand
    def markAction(self, request):
        raise

    @osAppCommand
    def gotoMarkAction(self, request):
        raise

    @osAppCommand
    def moveDownAction(self, request):
        return 'xdotool getactivewindow key {repeat}j'

    @osAppCommand
    def moveUpAction(self, request):
        return 'xdotool getactivewindow key {repeat}k'

    @osAppCommand
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow key {repeat}h'

    @osAppCommand
    def moveRightAction(self, request):
        return 'xdotool getactivewindow key {repeat}l'

    @osAppCommand
    def forwardAction(self, request):
        return 'xdotool getactivewindow key {repeat}ctrl+f'

    @osAppCommand
    def backwardAction(self, request):
        return 'xdotool getactivewindow key {repeat}ctrl+b'

if __name__=='__main__':
    app=VimMode(port=33333, parent_port=44444)
    app.run()

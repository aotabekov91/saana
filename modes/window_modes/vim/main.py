import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.helper import osAppCommand

from speechToCommand.modes.window_modes.generic import GenericMode 

class VimMode(GenericMode):
    def __init__(self, keyword='vimmode', info='VimMode', port=None, parent_port=None, config=None, window_classes=[]):
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
        return 'xdotool getactivewindow key j'

    @osAppCommand
    def moveUpAction(self, request):
        return 'xdotool getactivewindow key k'

    @osAppCommand
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow key h'

    @osAppCommand
    def moveRightAction(self, request):
        return 'xdotool getactivewindow key l'

    @osAppCommand
    def forwardAction(self, request):
        return 'xdotool getactivewindow key ctrl+f'

    @osAppCommand
    def backwardAction(self, request):
        return 'xdotool getactivewindow key ctrl+b'

if __name__=='__main__':
    app=VimMode(port=33333, parent_port=44444)
    app.run()

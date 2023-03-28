import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import GenericMode

class FehMode(GenericMode):
    def __init__(self,
                 keyword='feh', 
                 info='FehMode', 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 window_classes=['feh']):

        super(FehMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

    @command()
    def toggleAction(self, request={}):
        return 'xdotool getactivewindow type h'

    @command()
    def plusAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} alt+Right'

    @command()
    def minusAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} alt+Left'

    @command()
    def topAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} alt+Up'

    @command()
    def bottomAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} alt+Down'

    @command()
    def informationAction(self, request={}):
        return 'xdotool getactivewindow type i'

if __name__=='__main__':
    app=FehMode(port=33333, parent_port=44444)
    app.run()

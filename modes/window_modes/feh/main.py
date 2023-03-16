import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import osAppCommand
from speechToCommand.utils.moder import BaseGenericMode

class FehMode(BaseGenericMode):
    def __init__(self,
                 keyword='vimmode', 
                 info='VimMode', 
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

    @osAppCommand()
    def playAction(self, request={}):
        return 'xdotool getactivewindow type h'

    @osAppCommand()
    def informationAction(self, request={}):
        return 'xdotool getactivewindow type i'

if __name__=='__main__':
    app=FehMode(port=33333, parent_port=44444)
    app.run()

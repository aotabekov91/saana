import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import GenericMode

class VimMode(GenericMode):
    def __init__(self,
                 keyword='vim', 
                 info='VimMode', 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 window_classes=['vim']):

        super(VimMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

    @command()
    def markSetAction(self, request={}):
        self.editorAction({'request':'setTextInitialsAction'})
        return 'xdotool getactivewindow type m'

    @command()
    def markJumpAction(self, request):
        self.editorAction({'request':'setTextInitialsAction'})
        return f"xdotool getactivewindow type '`'"

    @command()
    def hintJumpAction(self, request):
        self.editorAction({'request':'setTextInitialsAction'})
        return 'xdotool getactivewindow type ..w'

    @command()
    def downAction(self, request):
        return 'xdotool getactivewindow type {repeat}j'

    @command()
    def upAction(self, request):
        return 'xdotool getactivewindow type {repeat}k'

    @command()
    def leftAction(self, request):
        return 'xdotool getactivewindow type {repeat}h'

    @command()
    def rightAction(self, request):
        return 'xdotool getactivewindow type {repeat}l'

    @command()
    def gotoBeginAction(self, request={}):
        return 'xdotool getactivewindow key --repeat 2 g'

    @command()
    def gotoEndAction(self, request={}):
        return 'xdotool getactivewindow type G'

    @command()
    def copyAction(self, request={}):
        return 'xdotool getactivewindow key Ctrl+Shift+c'

    @command()
    def pasteAction(self, request={}):
        return 'xdotool getactivewindow key Ctrl+Shift+v'

    @command()
    def searchAction(self, request={}):
        self.editorAction({'request': 'setTextAction'})
        return 'xdotool getactivewindow type /' 

    @command()
    def yankAction(self, request={}):
        return 'xdotool getactivewindow type yy' 

    @command()
    def putAction(self, request={}):
        return 'xdotool getactivewindow type p' 

if __name__=='__main__':
    app=VimMode(port=33333, parent_port=44444)
    app.run()

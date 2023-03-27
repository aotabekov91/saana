import re
import os
import sys
import time

import subprocess

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import QBaseGenericMode

class InputMode(QBaseGenericMode):
    def __init__(self, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 keyword='inputer', 
                 info='Input', 
                 window_classes='all',
                 ):
        super(InputMode, self).__init__(
                 keyword=keyword,
                 info=info,
                 port=port, 
                 parent_port=parent_port, 
                 config=config, 
                 window_classes=window_classes)

    @command()
    def tabAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Tab'

    @command()
    def escapeAction(self, request):
        return 'xdotool getactivewindow key Escape'
  
    @command()
    def enterAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @command()
    def spaceAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @command()
    def backspaceAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} BackSpace'

    @command()
    def interuptAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+c'

    def saveToClipboardAction(self, request={}):
        slot_names=request['slot_names']
        text=slot_names.get('text', None)
        if text:
            self.clipboard().setText(text)

    @command()
    def copyAction(self, request):
        return 'xdotool getactivewindow key ctrl+c'

    @command()
    def pasteAction(self, request={}):
        return 'xdotool getactivewindow key ctrl+v'

    @command()
    def changeKeyboard(self, request):
        lan=request['slot_names']['lan']
        return f'setxkbmap {lan}' 

    @command(checkWindowType=False)
    def downAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Down'

    @command(checkWindowType=False)
    def upAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Up'

    @command(checkWindowType=False)
    def leftAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Left'

    @command(checkWindowType=False)
    def rightAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Right'


if __name__=='__main__':
    app=InputMode(port=33333)
    app.run()

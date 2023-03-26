import re
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.helper import osAppCommand

class ClipboardMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ClipboardMode, self).__init__(
                 keyword='clipboard', 
                 info='Clipboard', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config, 
                 window_classes='all')

    def saveToClipboardAction(self, request={}):
        slot_names=request['slot_names']
        text=slot_names.get('text', None)
        if text:
            self.clipboard().setText(text)

    @osAppCommand(checkWindowType=False)
    def copyAction(self, request):
        window=self.get_current_window()
        if window.window_class in ['kitty', 'tmux']:
            return 'xdotool key ctrl+shift+c'
        else:
            return 'xdotool getactivewindow key ctrl+c'

    @osAppCommand(checkWindowType=False)
    def pasteAction(self, request={}):
        window=self.get_current_window()
        if window.window_class in ['kitty', 'tmux']:
            return 'xdotool getactivewindow key ctrl+shift+v'
        else:
            return 'xdotool getactivewindow key ctrl+v'

if __name__=='__main__':
    app=ClipboardMode(port=33333)
    app.run()

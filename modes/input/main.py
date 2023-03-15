import re
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qinput import InputMainWindow

class InputMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(InputMode, self).__init__(
                 keyword='inputer', 
                 info='Input', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config, 
                 window_classes='all')

        self.client=None
        self.ui=InputMainWindow(self, 'AppsMode - own_floating', 'Apps: ')

    def set_mode(self, mode_name):
        if self.parent_socket:
            self.parent_socket.send_json(
                    {'command':'setCurrentMode', 'mode_name':mode_name})
            respond=self.parent_socket.recv_json()
            print(respond)

    def showAction(self, request={}):
        self.set_mode(self.__class__.__name__)
        self.client=request['slot_names'].get('client', None)
        self.action=request['slot_names'].get('action', None)
        self.ui.show()
        self.ui.edit.setFocus()

    def writeAction(self, request={}):
        slot_names=request['slot_names']
        text=slot_names.get('input', '')
        edit_text=self.ui.edit.text()
        new_text=' '.join([edit_text, text])
        new_text=re.sub('  *', ' ', new_text)
        self.ui.edit.setText(new_text)
        self.ui.show()
        self.ui.edit.setFocus()

    def confirmAction(self, request={}):
        if self.ui.isVisible():
            text=self.ui.edit.text()
            self.ui.edit.clear()
            self.ui.hide()
            time.sleep(0.1)

            if self.parent_port:
                self.set_mode(self.client)
                self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name': self.client,
                    'mode_action': self.action,
                    'slot_names': {'text':text},
                    })
                print(self.parent_socket.recv_json())


if __name__=='__main__':
    app=InputMode(port=33333)
    app.run()

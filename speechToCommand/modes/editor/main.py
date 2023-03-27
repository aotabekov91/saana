import re
import os
import sys
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from ..generic import GenericMode 

from speechToCommand.utils.helper import command
from speechToCommand.utils.widgets.qinput import InputMainWindow

class EditorMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(EditorMode, self).__init__(
                 keyword='editor', 
                 info='Editor', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.client=None
        self.client_action=None
        self.client_request=[]

        self.ui=InputMainWindow(self, 'InputMode - own_floating', 'Inputs: ')
        self.ui.setFixedSize(700, 30)

    def write_text(self, text):
        if 'setTextInitialsAction' in self.client_request:
            text=''.join([f[0] for f in text.split(' ') if len(f)>0])
        self.ui.edit.setText(text)

    def send_text(self, text, delay=0.01):
        time.sleep(delay)
        if self.parent_port and self.client:
            self.parent_socket.send_json({
                'command': 'setModeAction',
                'mode_name': self.client,
                'mode_action': self.client_action,
                'slot_names': {'text':text},
                })
            respond=self.parent_socket.recv_json()

    def activateAction(self, request={}):
        self.client=request['slot_names'].get('client', None)
        self.client_action=request['slot_names'].get('action', None)
        self.client_request=request['slot_names'].get('request', [])
        delay=request['slot_names'].get('delay', None)
        if delay: time.sleep(delay)
        self.ui.showAction(request)
        self.lockAction(request)

    @command(checkActionOnFinish=True)
    def escapeAction(self, request):
        self.client=None
        self.client_action=None
        self.client_request=[]
        self.unlockAction(request)

    def lockListen(self, request):
        text=request['slot_names']['text']
        slots=request['slot_names']['slots']
        action=request['slot_names']['command']
        if action:
            command=action.split('_')[-1]
            action=getattr(self, command, None)
            if not action:
                action=getattr(self.ui, command, None)
        if action:
            action({'slot_names':slots})
        else:
            self.write_text(f'{self.ui.edit.text()} {text.strip()}')

    def confirmAction(self, request={}):
        text=self.ui.edit.text().strip()
        self.ui.edit.clear()
        self.ui.hide()
        if 'setTextAction' in self.client_request:
            self.setTextAction({'text':text})
        elif 'setTextInitialsAction' in self.client_request:
            self.setTextAction({'text':text})
        if 'sendTextAction' in self.client_request:
            self.send_text(text)
        if 'clickEnter' in self.client_request:
            self.enterAction(request)
        self.escapeAction(request)

    @command(checkWindowType=False)
    def setTextAction(self, request):
        text=request['text']
        return f'xdotool getactivewindow type "{text}"'

    @command()
    def removeAction(self, request):
        # todo remove words and sentences in any app
        slot_names=request['slot_names']
        unit=slot_names.get('unit', None)
        if unit: 
            if unit=='word':
                print('have to remove word')
            elif unit=='sentence':
                print('have to remove sentece')
            elif unit=='paragraph':
                print('have to remove paragraph')
        else:
            super().removeAction(request)

if __name__=='__main__':
    app=EditorMode(port=33333)
    app.run()

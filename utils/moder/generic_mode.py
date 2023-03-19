import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from .base_mode import BaseMode
from speechToCommand.utils.helper import osGenericCommand

class BaseGenericMode(BaseMode):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 window_classes='all',
                 argv=None):

        super(BaseGenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                argv=argv,
                window_classes=window_classes,
                )

    def confirmAction(self, request):
        os.popen('xdotool getactivewindow key Enter')
        self.checkAction(request)

    @osGenericCommand
    def cancelAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Escape'

    @osGenericCommand
    def forwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @osGenericCommand
    def backwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} shift+space'

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))
    
    @osGenericCommand
    def zoomInAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} plus'

    @osGenericCommand
    def removeAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} BackSpace'

    @osGenericCommand
    def zoomOutAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} minus'

    @osGenericCommand
    def moveDownAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Down'

    @osGenericCommand
    def moveUpAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Up'

    @osGenericCommand
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Left'

    @osGenericCommand
    def moveRightAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Right'

    @osGenericCommand
    def pasteAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+v'

    @osGenericCommand
    def copyAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+c'

    def floatingToggleAction(self, request):
        asyncio.run(self.manager.command('floating toggle'))

    def checkAction(self, request={}, delay=0.05):
        if self.parent_port:
            time.sleep(delay)
            self.parent_socket.send_json(
                    {'command':'setCurrentWindow',
                     'request': request})
            return self.parent_socket.recv_json()

    def activateInput(self, func_name, delay_show=0.01): 
        if self.parent_port:
            self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name' : 'InputMode',
                    'mode_action': 'activateAction',
                    'slot_names':
                        {
                        'client': self.__class__.__name__,
                        'action': func_name,
                        'delay': delay_show,
                        }
                    })
            print(self.parent_socket.recv_json())

    def closeAction(self, request):
        asyncio.run(self.manager.command('kill'))
        self.checkAction(request)

    def hideAction(self, request):
        asyncio.run(self.manager.command('move scratchpad'))
        self.checkAction(request)

    def doneAction(self, request):
        self.hideAction(request)
        self.checkAction(request)

    @osGenericCommand
    def inputAction(self, request):
        if self.parent_port:
            self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name' : 'InputMode',
                    'mode_action': 'activateAction',
                    'slot_names': {'client': self.__class__.__name__,
                                   'action':'setInputAction'}
                    })
            print(self.parent_socket.recv_json())

    @osGenericCommand
    def setInputAction(self, request):
        slot_names=request['slot_names']
        text=slot_names.get('text', '')
        cmd=f'xdotool getactivewindow type "{text}"'
        return cmd
    
    def getTextAction(self, request):
        slot_names=request['slot_names']
        return slot_names.get('text', '').strip()

    @osGenericCommand
    def setTextAction(self, request):
        text=self.getTextAction(request)
        if text: return f'xdotool getactivewindow type {text}'

    @osGenericCommand
    def setTextInitialsAction(self, request):
        text=self.getTextAction(request)
        if text:
            text=''.join([h[0] for h in text.split(' ') if h!=''])
            return f'xdotool getactivewindow type {text}'

    def repeat(self, request):
        slot_names=request.get('slot_names', {})
        return slot_names.get('repeat', 1)
        
if __name__=='__main__':
    app=BaseGenericMode(port=33333, parent_port=44444)
    app.run()

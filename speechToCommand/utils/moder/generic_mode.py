import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from .base_mode import BaseMode
from ..helper import command

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
                window_classes=window_classes,
                argv=argv,
                )

    def repeat(self, request):
        slot_names=request.get('slot_names', {})
        return slot_names.get('repeat', 1)

    def checkAction(self, request={}, delay=0.05):
        if self.parent_port:
            time.sleep(delay)
            self.parent_socket.send_json(
                    {'command':'setCurrentWindow',
                     'request': request})
            return self.parent_socket.recv_json()

    def dictateAction(self, slot_names, delay_show=0.05): 
        if self.parent_port:
            slot_names['client']=self.__class__.__name__
            slot_names['delay']=delay_show
            self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name' : 'EditorMode',
                    'mode_action': 'activateAction',
                    'slot_names':slot_names,
                    })
            print(self.parent_socket.recv_json())

    @command(checkWindowType=True)
    def confirmAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @command(checkWindowType=False)
    def cancelAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Escape'

    @command(checkWindowType=False)
    def forwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+f'

    @command(checkWindowType=False)
    def backwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+b'

    @command(checkWindowType=False)
    def nextAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @command(checkWindowType=False)
    def previousAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} shift+space'

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))
    
    @command(checkWindowType=False)
    def zoomInAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} plus'

    @command(checkWindowType=False)
    def zoomOutAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} minus'

if __name__=='__main__':
    app=BaseGenericMode(port=33333, parent_port=44444)
    app.run()

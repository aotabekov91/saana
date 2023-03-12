import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.helper import osGenericCommand

class GenericMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(GenericMode, self).__init__(
                keyword='generic',
                info='Generic commands',
                port=port,
                parent_port=parent_port,
                config=config
                )
        self.current_window=None

    def handle_request(self, request):
        try:
            print(f'{self.__class__.__name__} received request: {request}')
            command=request['command'].split('_')[-1]
            action=getattr(self, command, False)
            if action:
                action(request)
                msg={"status":f"{self.__class__.__name__} handled request"}
            else:
                msg={"status":"not understood"}
        except:
            err_type, error, traceback = sys.exc_info()
            msg='{err}'.format(err=error)

        print(msg)

    def handleCustomRequest(self, request):
        print(f'{self.__class__.__name__}: handling custom request')
        request=request['intent_data']
        command=request['command'].split('_')[-1]
        action=getattr(self, command, False)
        if action: action(request)

    def run_command(self, command, container=None):
        if container:
            asyncio.run(container.command(command))
        else:
            asyncio.run(self.manager.command(command))

    def set_current_window(self):
        tree=asyncio.run(self.manager.get_tree())
        self.current_window=tree.find_focused()

    def showAction(self, request):
        if self.current_window:
            asyncio.run(self.current_window.command('focus'))
            self.current_window=None

    def floatingToggleAction(self, request):
        asyncio.run(self.manager.command('floating toggle'))

    def closeAction(self, request):
        asyncio.run(self.manager.command('kill'))
        time.sleep(.1)
        self.checkAction(request)

    def hideAction(self, request):
        self.set_current_window()
        self.run_command('move scratchpad')
        time.sleep(0.1)
        self.checkAction(request)

    def doneAction(self, request):
        self.hideAction(request)
        time.sleep(.1)
        self.checkAction(request)

    @osGenericCommand
    def copyAction(self, request):
        class_=os.popen('xdotool getactivewindow getwindowclassname')
        if class_ in ['kitty']:
            return 'xdotool getactivewindow key ctrl+c'
        else:
            return 'xdotool getactivewindow key ctrl+shift+c'

    @osGenericCommand
    def pasteAction(self, request):
        class_=os.popen('xdotool getactivewindow getwindowclassname')
        if class_ in ['kitty']:
            return 'xdotool getactivewindow key ctrl+v'
        else:
            return 'xdotool getactivewindow key ctrl+shift+v'

    @osGenericCommand
    def removeAction(self, request):
        return 'xdotool getactivewindow key BackSpace'

    @osGenericCommand
    def moveDownAction(self, request):
        return 'xdotool getactivewindow key Down'

    @osGenericCommand
    def moveUpAction(self, request):
        return 'xdotool getactivewindow key Up'

    @osGenericCommand
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow key Left'

    @osGenericCommand
    def moveRightAction(self, request):
        return 'xdotool getactivewindow key Right'

    def confirmAction(self, request):
        os.popen('xdotool getactivewindow key Enter')
        time.sleep(.1)
        self.checkAction(request)

    @osGenericCommand
    def escapeAction(self, request):
        return 'xdotool getactivewindow key Escape'

    @osGenericCommand
    def forwardAction(self, request):
        return 'xdotool getactivewindow key space'

    @osGenericCommand
    def backwardAction(self, request):
        return 'xdotool getactivewindow key shift+space'

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))
    
    @osGenericCommand
    def zoomInAction(self, request={}):
        return f'xdotool getactivewindow type +'

    @osGenericCommand
    def zoomOutAction(self, request={}):
        return f'xdotool getactivewindow type -'

    @osGenericCommand
    def inputAction(self, request):
        slot_names=request.get('slot_names', {})
        text=slot_names.get('input', '')
        return f'xdotool getactivewindow type {text}'
        
    def checkAction(self, request):
        self.set_current_window()
        window_class=self.current_window.window_class
        if not self.parent_port: return
        if not self.config.has_section('Custom'): return
        if not self.config.has_option('Custom', window_class): return

        mode_name=self.config.get('Custom', window_class)

        self.parent_socket.send_json(
                {'command':'setCurrentMode',
                 'mode_name':mode_name})
        respond=self.parent_socket.recv_json()
        print(respond)

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

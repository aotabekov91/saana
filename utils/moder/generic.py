import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import osGenericCommand

class GenericWindow:

    def __init__(self, parent=None):
        self.parent=parent
        self.current_window=None
        self.manager=asyncio.run(Connection().connect())

    def handle_request(self, request):
        print(f'{self.__class__.__name__}: UI handling request')
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

    def copyAction(self, request):
        class_=os.popen('xdotool getactivewindow getwindowclassname')
        if class_ in ['kitty']:
            os.popen('xdotool getactivewindow key ctrl+c')
        else:
            os.popen('xdotool getactivewindow key ctrl+shift+c')

    def pasteAction(self, request):
        class_=os.popen('xdotool getactivewindow getwindowclassname')
        if class_ in ['kitty']:
            os.popen('xdotool getactivewindow key ctrl+v')
        else:
            os.popen('xdotool getactivewindow key ctrl+shift+v')

    def removeAction(self, request):
        os.popen('xdotool getactivewindow key BackSpace')

    # def moveDownAction(self, request):
    #     os.popen('xdotool getactivewindow key Down')

    @osGenericCommand
    def moveDownAction(self, request):
        return 'xdotool getactivewindow key Down'

    def moveUpAction(self, request):
        os.popen('xdotool getactivewindow key Up')

    def moveLeftAction(self, request):
        os.popen('xdotool getactivewindow key Left')

    def moveRightAction(self, request):
        os.popen('xdotool getactivewindow key Right')

    def confirmAction(self, request):
        os.popen('xdotool getactivewindow key Enter')
        time.sleep(.1)
        self.checkAction(request)

    def escapeAction(self, request):
        os.popen('xdotool getactivewindow key Escape')

    def forwardAction(self, request):
        os.popen('xdotool getactivewindow key space')

    def backwardAction(self, request):
        os.popen('xdotool getactivewindow key shift+space')

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))
    
    def zoomInAction(self, request={}):
        os.popen(f'xdotool getactivewindow type +')

    def zoomOutAction(self, request={}):
        os.popen(f'xdotool getactivewindow type -')

    def inputAction(self, request):
        slot_names=request.get('slot_names', {})
        text=slot_names.get('input', '')
        os.popen('xdotool getactivewindow type {text}')
        
    def checkAction(self, request):
        self.set_current_window()
        window_class=self.current_window.window_class
        if not self.parent.parent_port: return
        if not self.parent.config.has_section('Custom'): return
        if not self.parent.config.has_option('Custom', window_class): return

        mode_name=self.parent.config.get('Custom', window_class)

        self.parent.parent_socket.send_json(
                {'command':'setCurrentMode',
                 'mode_name':mode_name})
        respond=self.parent.parent_socket.recv_json()
        print(respond)

    def check_window_class(self):
        self.set_current_window()
        if self.current_window.window_class==self.parent.window_class:
            return True
        else:
            self.checkAction({})

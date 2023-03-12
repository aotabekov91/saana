import os
import sys
import zmq
import time
import subprocess

import asyncio
from i3ipc.aio import Connection

class GenericWindow:

    def __init__(self, parent_port=None):
        self.current_window=None
        self.parent_port=parent_port
        self.manager=asyncio.run(Connection().connect())
        self.set_connection()

    def set_connection(self):
        if self.parent_port:
            self.parent_socket=zmq.Context().socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.parent_port}')

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
        time.sleep(1)
        if self.parent_port:
            self.parent_socket.send_json({'command':'setModeAction',
                                          'mode_name':'CheckerMode',
                                          'mode_action':'checkAction',
                                          })
            respond=self.parent_socket.recv_json()
            print(respond)


    def hideAction(self, request):
        self.set_current_window()
        self.run_command('move scratchpad')

    def doneAction(self, request):
        self.hideAction(request)
        time.sleep(1)
        if self.parent_port:
            self.parent_socket.send_json({'command':'setModeAction',
                                          'mode_name':'CheckerMode',
                                          'mode_action':'checkAction',
                                          })
            respond=self.parent_socket.recv_json()
            print(respond)


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

    def moveDownAction(self, request):
        os.popen('xdotool getactivewindow key Down')

    def moveUpAction(self, request):
        os.popen('xdotool getactivewindow key Up')

    def moveLeftAction(self, request):
        os.popen('xdotool getactivewindow key Left')

    def moveRightAction(self, request):
        os.popen('xdotool getactivewindow key Right')

    def confirmAction(self, request):
        os.popen('xdotool getactivewindow key Enter')
        time.sleep(1)
        if self.parent_port:
            self.parent_socket.send_json({'command':'setModeAction',
                                          'mode_name':'CheckerMode',
                                          'mode_action':'checkAction',
                                          })
            respond=self.parent_socket.recv_json()
            print(respond)

    def escapeAction(self, request):
        os.popen('xdotool getactivewindow key Escape')

    def forwardAction(self, request):
        os.popen('xdotool getactivewindow key space')

    def backwardAction(self, request):
        os.popen('xdotool getactivewindow key shift+space')

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))

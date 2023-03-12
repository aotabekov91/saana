import os
import sys
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode

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
        self.manager=asyncio.run(Connection().connect())

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

    def hideAction(self, request):
        self.set_current_window()
        self.run_command('move scratchpad')

    def doneAction(self, request):
        self.hideAction(request)

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
        if self.parent_port:
            self.parent_socket.send_json({'command':'setModeAction',
                                          'mode_name':'CheckerMode',
                                          'mode_action':'checkAction',
                                          })
            respond=self.parent_socket.recv_json()
            print(respond)

    def cancelAction(self, request):
        os.popen('xdotool getactivewindow key Escape')

    def forwardAction(self, request):
        os.popen('xdotool getactivewindow key space')

    def backwardAction(self, request):
        os.popen('xdotool getactivewindow key shift+space')

    def inputAction(self, request):
        slot_names=request.get('slot_names', {})
        input_=slot_names.get('input', None)
        if input_: os.popen(f'xdotool getactivewindow type {input_}') 

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

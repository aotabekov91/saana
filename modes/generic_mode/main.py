import os
import sys
import asyncio
import subprocess

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

        self.connect_to_manager()

        self.current_window=None

    def connect_to_manager(self):
        self.manager=asyncio.run(Connection().connect())
        self.tree=asyncio.run(self.manager.get_tree())

    def run_command(self, command, container=None):
        if container:
            asyncio.run(container.command(command))
        else:
            asyncio.run(self.manager.command(command))

    def set_current_window(self):
        self.current_window=self.tree.find_focused()

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

    def escapeAction(self, request):
        os.popen('xdotool getactivewindow key Escape')

    def spaceAction(self, request):
        os.popen('xdotool getactivewindow key space')

    def spaceShiftAction(self, request):
        os.popen('xdotool getactivewindow key shift+space')

    def fullscreenAction(self, request):
        asyncio.run(self.manager.command('fullscreen toggle'))

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

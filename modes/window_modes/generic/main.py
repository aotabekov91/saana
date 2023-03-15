import os
import sys
import time

import asyncio

from speechToCommand.utils.helper import osGenericCommand

from speechToCommand.utils.window import BaseGenericMode

class GenericMode(BaseGenericMode):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 window_classes=[]):

        super(GenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

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
        asyncio.run(self.manager.command('move scratchpad'))
        time.sleep(0.1)
        self.checkAction(request)

    def doneAction(self, request):
        self.hideAction(request)
        time.sleep(.1)
        self.checkAction(request)

    def repeat(self, request):
        slot_names=request['slot_names']
        return slot_names.get('repeat', 1)

    @osGenericCommand
    def copyAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+c'

    @osGenericCommand
    def pasteAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+v'

    @osGenericCommand
    def removeAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} BackSpace'

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

    def confirmAction(self, request):
        os.popen('xdotool getactivewindow key --repeat {repeat} Enter')
        time.sleep(.1)
        self.checkAction(request)

    @osGenericCommand
    def escapeAction(self, request):
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
    def zoomOutAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} minus'

    def inputAction(self, request):
        if self.parent_port:
            self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name' : 'InputMode',
                    'mode_action': 'showAction',
                    'slot_names': {'client': self.__class__.__name__,
                                   'action':'setInputAction'}
                    })
            print(self.parent_socket.recv_json())

    @osGenericCommand
    def setInputAction(self, request):
        slot_names=request['slot_names']
        text=slot_names.get('text', '')
        cmd=f'xdotool getactivewindow type {text}'
        print(cmd)
        return cmd

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

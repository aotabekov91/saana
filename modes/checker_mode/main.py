import os
import sys
import subprocess

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode

class CheckerMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(CheckerMode, self).__init__(
                 keyword='check', 
                 info='Checker', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.manager=asyncio.run(Connection().connect())

    def checkAction(self, request):

        self.generic.set_current_window()
        window_class=self.generic.current_window.window_class

        if not window_class in ['qutebrowser']: return

        if 'qutebrowser'==window_class:

            mode_name='QutebrowserMode'

        self.parent_socket.send_json({'command':'setCurrentMode',
                                      'mode_name':mode_name})
        respond=self.parent_socket.recv_json()
        print(respond)

        self.parent_socket.send_json({'command':'setModeAction',
                                      'mode_name':mode_name,
                                      'slot_names': 'activateMode'
                                      })
        respond=self.parent_socket.recv_json()
        print(respond)


if __name__=='__main__':
    app=CheckerMode(port=33333, parent_port=8888)
    app.run()

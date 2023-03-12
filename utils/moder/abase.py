import os
import sys
import subprocess

import asyncio
from i3ipc.aio import Connection

from .base import BaseMode

class ABaseMode(BaseMode):

    def __init__(self, keyword, info, window_class, port=None, parent_port=None, config=None):
        super(ABaseMode, self).__init__(
                 keyword=keyword,
                 info=info,
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.window_class=window_class
        self.manager=asyncio.run(Connection().connect())

    def check_window_class(self):
        self.generic.set_current_window()
        if self.generic.current_window.window_class==self.window_class:
            return True
        else:
            if self.parent_port:
                self.parent_socket.send_json({'command':'setModeAction',
                                              'mode_name':'CheckerMode',
                                              'mode_action':'checkAction',
                                              })
                respond=self.parent_socket.recv_json()
                print(respond)
            return False

    def command(self, func):
        def inner(self, request):
            if self.check_window_class():
                cmd=func(self, request)
                if cmd: os.popen(cmd)
        return inner 

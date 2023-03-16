import os
import sys
import asyncio
import subprocess

from i3ipc.aio import Connection

from speechToCommand.utils.helper import osAppCommand
from speechToCommand.utils.moder import BaseGenericMode

class WindowsMode(BaseGenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(WindowsMode, self).__init__(
                 keyword='windows', 
                 info='Windows manager', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.manager=asyncio.run(Connection().connect())

    def focusAction(self, request):
        slot_names=request.get('slot_names', {})
        window=slot_names.get('window', None)
        if window in ['left', 'right']:
            asyncio.run(self.manager.command(f'focus {window}'))
        self.checkAction()

    @osAppCommand()
    def hintJumpAction(self, request):
        self.activateInput('setTextInitialsAction')
        return 'i3-easyfocus -a'

    def changeWorkspaceAction(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            asyncio.run(self.manager.command(f'workspace {workspace}'))
            self.checkAction(request)

    def moveToWorkspaceAction(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            command=f'move container to workspace {workspace}; workspace {workspace}'
            asyncio.run(self.manager.command(command))

if __name__=='__main__':
    app=WindowsMode(port=8234)
    app.run()

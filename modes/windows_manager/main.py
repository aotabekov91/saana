import sys
import asyncio
import subprocess

from i3ipc.aio import Connection

from speechToCommand.utils.moder import BaseMode

class WindowsMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(WindowsMode, self).__init__(
                 keyword='windows', 
                 info='Windows manager', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.manager=asyncio.run(Connection().connect())

    def workspaceLeft(self, request):
        pass

    def workspaceRight(self, request):
        pass

    def changeWorkspace(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            asyncio.run(self.manager.command(f'workspace {workspace}'))

    def moveToWorkspace(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            command=f'move container to workspace {workspace}; workspace {workspace}'
            asyncio.run(self.manager.command(command))

    def runApplication(self, request):
        slot_names=request['slot_names']
        app=slot_names.get('app', None)
        if app:
            floating='--class floating'*(app=='kitty')
            command=f'exec {app} {floating}' 
            asyncio.run(self.manager.command(command))

    def runCommand(self, request):
        slot_names=request['slot_names']
        command=slot_names.get('command', None)
        if command:
            asyncio.run(self.manager.command(command))

if __name__=='__main__':
    app=WindowsMode(port=8234)
    app.run()

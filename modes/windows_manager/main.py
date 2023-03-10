import sys
import asyncio
import subprocess
from i3ipc.aio import Connection

from speechToCommand.utils.moder import Mode

from speechToCommand.utils.moder import BaseMode

class WindowsMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(WindowsMode, self).__init__(
                 keyword='windows', 
                 info='Windows manager', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        asyncio.run(self.connect_to_i3())

    def changeWorkspace(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            asyncio.run(self.run_command(f'workspace {workspace}'))

    def moveToWorkspace(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            command=f'move container to workspace {workspace}; workspace {workspace}'
            asyncio.run(self.run_command(command))

    def runApplication(self, request):
        slot_names=request['slot_names']
        app=slot_names.get('app', None)
        if app:
            floating='--class floating'*(app=='kitty')
            command=f'exec {app} {floating}' 
            asyncio.run(self.run_command(command))

    def runCommand(self, request):
        slot_names=request['slot_names']
        command=slot_names.get('command', None)
        if command:
            asyncio.run(self.run_command(command))

    async def connect_to_i3(self):
        self.i3=await Connection().connect()

    async def run_command(self, command):
        await self.i3.command(command)

if __name__=='__main__':
    app=WindowsMode(port=8234)
    app.run()

import os
import sys
import asyncio
import subprocess

from i3ipc.aio import Connection

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import GenericMode

class WindowsMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(WindowsMode, self).__init__(
                 keyword='windows', 
                 info='Windows manager', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

    @command()
    def hintJumpAction(self, request):
        self.activateInput('setTextInitialsAction')
        return 'i3-easyfocus -a'

    @command(checkActionOnFinish=True, windowCommand=True)
    def focusAction(self, request):
        slot_names=request.get('slot_names', {})
        window=slot_names.get('direction', None)
        if window in ['tiling', 'floating']:
            return 'focus mode_toggle'
        elif window in ['left', 'right']:
            workspaces=asyncio.run(self.manager.get_workspaces())
            for w in workspaces:
                if not w.visible: continue
                if window=='left' and w.num%2==0:
                    return f'workspace {w.num}'
                elif window=='right' and w.num%2==1:
                    return f'workspace {w.num}'

    @command(checkActionOnFinish=True, windowCommand=True)
    def changeWorkspaceAction(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            return f'workspace {int(workspace)}'

    @command(checkActionOnFinish=True, windowCommand=True)
    def moveToWorkspaceAction(self, request):
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            workspace=int(workspace)
            return f'move container to workspace {workspace}; workspace {int(workspace)}'

    @command(windowCommand=True)
    def floatingToggleAction(self, request):
        return 'floating toggle'

    @command(checkActionOnFinish=True, windowCommand=True)
    def hideAction(self, request):
        print('scratchpad')
        return 'move scratchpad'

    @command(checkActionOnFinish=True, windowCommand=True, waitAction=0.1)
    def closeAction(self, request):
        return 'kill'

if __name__=='__main__':
    app=WindowsMode(port=8234)
    app.run()

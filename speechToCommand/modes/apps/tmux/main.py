import os

from speechToCommand.utils.helper import command
from ..vim import VimMode

class TmuxMode(VimMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(TmuxMode, self).__init__(
                 keyword='tmux', 
                 info='Tmux', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['tmux'])

    @command(checkWindowType=False)
    def downAction(self, request):
        return 'tmux select-pane -D'

    @command(checkWindowType=False)
    def upAction(self, request):
        return 'tmux select-pane -U'

    @command(checkWindowType=False)
    def leftAction(self, request):
        return 'tmux select-pane -L'

    @command(checkWindowType=False)
    def rightAction(self, request):
        return 'tmux select-pane -R'

    @command(checkWindowType=False)
    def previousAction(self, request):
        return 'tmux previous-window'

    @command(checkWindowType=False)
    def nextAction(self, request):
        return 'tmux next-window'

    @command(checkWindowType=False)
    def hintJumpAction(self, request):
        return 'tmux display-panes'

    @command(checkWindowType=False)
    def changeWorkspaceAction(self, request):
        print(request)
        slot_names=request['slot_names']
        workspace=slot_names.get('workspace', None)
        if workspace:
            return f'xdotool getactivewindow type {int(workspace)}'

    @command(checkWindowType=False)
    def createAction(self, request):
        return 'tmux new-window'

    @command(checkWindowType=False)
    def searchAction(self, request):
        self.editorAction({'request':'setTextAction'})
        return 'xdotool getactivewindow key ctrl+a f'

    @command(checkWindowType=False)
    def renameAction(self, request):
        self.editorAction({'request':'setTextAction'})
        return 'xdotool getactivewindow key ctrl+a ,'

    @command(checkWindowType=False)
    def listAction(self, request):
        return 'xdotool getactivewindow key ctrl+a w'

    @command(checkWindowType=False)
    def horizontalAction(self, request):
        return 'tmux split-window -h'

    @command(checkWindowType=False)
    def verticalAction(self, request):
        return 'tmux split-window -v'

if __name__=='__main__':
    app=TmuxMode(port=33333)
    app.run()

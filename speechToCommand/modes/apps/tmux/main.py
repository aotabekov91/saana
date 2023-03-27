import os

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import BaseGenericMode

class TmuxMode(BaseGenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(TmuxMode, self).__init__(
                 keyword='tmux', 
                 info='Tmux', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['tmux'])

    @command()
    def downAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Down' 

    @command()
    def upAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Up' 

    @command()
    def leftAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Left'

    @command()
    def rightAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Right'

    @command()
    def createAction(self, request):
        pass

if __name__=='__main__':
    app=TmuxMode(port=33333)
    app.run()

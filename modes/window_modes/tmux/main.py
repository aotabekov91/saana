import os

from speechToCommand.utils.helper import osAppCommand
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

    @osAppCommand(checkWindowType=False)
    def moveDownAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Down' 

    @osAppCommand(checkWindowType=False)
    def moveUpAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Up' 

    @osAppCommand(checkWindowType=False)
    def moveLeftAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Left'

    @osAppCommand(checkWindowType=False)
    def moveRightAction(self, request):
        return 'xdotool getactivewindow key ctrl+a Right'

    @osAppCommand(checkWindowType=False)
    def createAction(self, request):
        pass

if __name__=='__main__':
    app=TmuxMode(port=33333)
    app.run()

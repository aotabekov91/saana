from .base import BaseMode
from speechToCommand.utils.helper import command

class InputMode(BaseMode):

    @command(checkWindowType=False)
    def tabAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Tab'

    @command(checkActionOnFinish=True, checkWindowType=False)
    def escapeAction(self, request):
        return 'xdotool getactivewindow key Escape'
  
    @command(checkActionOnFinish=True, checkWindowType=False)
    def enterAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @command(checkWindowType=False)
    def spaceAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @command(checkWindowType=False)
    def backspaceAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} BackSpace'

    @command(checkWindowType=False)
    def interuptAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+c'

    @command(checkWindowType=False)
    def copyAction(self, request):
        return 'xdotool getactivewindow key ctrl+c'

    @command(checkWindowType=False)
    def pasteAction(self, request={}):
        return 'xdotool getactivewindow key ctrl+v'

    @command(checkWindowType=False)
    def changeKeyboardAction(self, request):
        lan=request['slot_names']['lan']
        return f'setxkbmap {lan}' 

    @command(checkWindowType=False)
    def downAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Down'

    @command(checkWindowType=False)
    def upAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Up'

    @command(checkWindowType=False)
    def leftAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Left'

    @command(checkWindowType=False)
    def rightAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Right'


if __name__=='__main__':
    app=InputMode(port=33333)
    app.run()

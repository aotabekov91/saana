from speechToCommand.utils.helper import command

from ..qutebrowser import QutebrowserMode

class ChromeMode(QutebrowserMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ChromeMode, self).__init__(
                 keyword='chrome', 
                 info='Google-chrome', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['Google-chrome'])

    @command()
    def showAction(self, request):
        return f'xdotool getactivewindow key shift+t' 

    @command()
    def tabAction(self, request):
        return f'xdotool getactivewindow key ctrl+t' 

    @command()
    def openAction(self, request):
        return f'xdotool getactivewindow type o " "'

    @command()
    def leftAction(self, request):
        return f'xdotool getactivewindow key shift+j'

    @command()
    def rightAction(self, request):
        return f'xdotool getactivewindow key shift+k'

    @command()
    def downAction(self, request):
        return f'xdotool getactivewindow key Down'

    @command()
    def upAction(self, request):
        return f'xdotool getactivewindow key Up'

    @command()
    def doneAction(self, request):
        return f'xdotool getactivewindow key ctrl+w'

    @command()
    def undoAction(self, request):
        return f'xdotool getactivewindow key shift+x'

if __name__=='__main__':
    app=ChromeMode(port=33333)
    app.run()

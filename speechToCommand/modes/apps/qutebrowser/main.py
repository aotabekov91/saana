import os

from speechToCommand.utils.helper import command

from ..vim import VimMode

class QutebrowserMode(VimMode):
    def __init__(self, keyword='browser', info='Qutebrowser', port=None, parent_port=None, config=None, window_classes=['qutebrowser']):
        super(QutebrowserMode, self).__init__(
                 keyword=keyword,
                 info=info,
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=window_classes)

    @command()
    def previousAction(self, request={}):
        return 'xdotool getactivewindow key shift+h'

    @command()
    def nextAction(self, request={}):
        return 'xdotool getactivewindow key shift+l'

    @command()
    def tabAction(self, request):
        return f'xdotool getactivewindow type o -t " "'

    @command()
    def openAction(self, request):
        return f'xdotool getactivewindow type o " "'

    @command()
    def moveLeftAction(self, request):
        return f'xdotool getactivewindow key shift+k'

    @command()
    def moveRightAction(self, request):
        return f'xdotool getactivewindow key shift+j'

    @command()
    def doneAction(self, request):
        return f'xdotool getactivewindow type d'

    @command()
    def refreshAction(self, request={}):
        return 'xdotool getactivewindow type r'

    @command()
    def hintJumpAction(self, request={}):
        super().hintJumpAction(request)
        return 'xdotool getactivewindow type f'

    @command()
    def hintJumpNewAction(self, request={}):
        self.activateInput(self.setTextInitialsAction)
        return f'xdotool getactivewindow type F'

if __name__=='__main__':
    app=QutebrowserMode(port=33333)
    app.run()

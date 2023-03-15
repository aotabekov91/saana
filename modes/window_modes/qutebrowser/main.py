import os

from speechToCommand.utils.helper import osAppCommand

from ..vim import VimMode

class QutebrowserMode(VimMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(QutebrowserMode, self).__init__(
                 keyword='browser', 
                 info='Qutebrowser', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['qutebrowser'])

    @osAppCommand
    def backwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+h'

    @osAppCommand
    def forwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+l'

    @osAppCommand
    def openTabAction(self, request):
        return f'xdotool getactivewindow type o -t " "'

    @osAppCommand
    def openAction(self, request):
        return f'xdotool getactivewindow type o " "'

    @osAppCommand
    def moveLeftAction(self, request):
        return f'xdotool getactivewindow key shift+j'

    @osAppCommand
    def moveRightAction(self, request):
        return f'xdotool getactivewindow key shift+k'

    @osAppCommand
    def doneAction(self, request):
        return f'xdotool getactivewindow type d'

    @osAppCommand
    def refreshAction(self, request={}):
        return 'xdotool getactivewindow type r'

    @osAppCommand
    def markAction(self, request={}):
        return 'xdotool getactivewindow type m'
    
    @osAppCommand
    def showHintAction(self, request={}):
        return f'xdotool getactivewindow type f'

    @osAppCommand
    def createHintAction(self, request={}):
        slot_names=request['slot_names']
        hint=slot_names.get('hint', None)
        os.popen(f'xdotool getactivewindow key Escape')
        os.popen(f'xdotool getactivewindow type F')
        if hint:
            hint=''.join([h[0] for h in hint.split(' ')])
            return f'xdotool getactivewindow type {hint}'

if __name__=='__main__':
    app=QutebrowserMode(port=33333)
    app.run()

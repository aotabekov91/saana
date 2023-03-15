import os

from speechToCommand.utils.helper import osAppCommand

from ..vim import VimMode

class SioyekMode(VimMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(SioyekMode, self).__init__(
                 keyword='document', 
                 info='Sioyek', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['sioyek'])

    @osAppCommand
    def backwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+h'

    @osAppCommand
    def forwardAction(self, request={}):
        return 'xdotool getactivewindow key shift+l'

    @osAppCommand
    def openAction(self, request):
        return f'xdotool getactivewindow type o -t " "'

    @osAppCommand
    def doneAction(self, request):
        return f'xdotool getactivewindow type d'

    @osAppCommand
    def markAction(self, request={}):
        return f'xdotool getactivewindow type m'
    
    @osAppCommand
    def showHintAction(self, request={}):
        return f'xdotool getactivewindow type f'

    @osAppCommand
    def followHintAction(self, request={}):
        slot_names=request['slot_names']
        hint=slot_names.get('hint', None)
        if hint:
            hint=''.join([h[0] for h in hint.split(' ')])
            return f'xdotool getactivewindow type {hint}'

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
    app=SioyekMode(port=33333)
    app.run()

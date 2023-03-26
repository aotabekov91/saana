import os

from sioyek import sioyek
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

        self.sioyek=sioyek.Sioyek(
                self.config.get('Custom', 'binary_path'),
                self.config.get('Custom', 'local_database_path'),
                self.config.get('Custom', 'shared_database_path'),
                )


    @osAppCommand()
    def backwardAction(self, request={}):
        self.sioyek.prev_state()

    @osAppCommand()
    def forwardAction(self, request={}):
        self.sioyek.next_state()

    @osAppCommand()
    def moveLeftAction(self, request={}):
        return 'xdotool getactivewindow  type {repeat}H'

    @osAppCommand()
    def moveRightAction(self, request={}):
        return 'xdotool getactivewindow  type {repeat}L'

    @osAppCommand()
    def openAction(self, request):
        self.sioyek.open_prev_doc()

    @osAppCommand()
    def openTabAction(self, request):
        return f'xdotool getactivewindow key Ctrl+o'

    @osAppCommand()
    def doneAction(self, request):
        self.sioyek.quit()

    @osAppCommand()
    def fitAction(self, request):
        return f'xdotool getactivewindow key equal'

    @osAppCommand()
    def hintJumpAction(self, request={}):
        super().showHintAction(request)
        return 'xdotool getactivewindow type v'

    @osAppCommand()
    def followHintAction(self, request={}):
        slot_names=request['slot_names']
        hint=slot_names.get('text', None)
        print(request)
        if hint:
            hint=hint.strip()
            hint=''.join([h[0] for h in hint.split(' ') if h!=''])
            print(hint)
            return f'xdotool getactivewindow type {hint}'

    @osAppCommand()
    def createHintAction(self, request={}):
        raise

if __name__=='__main__':
    app=SioyekMode(port=33333)
    app.run()

import os

from sioyek import sioyek
from speechToCommand.utils.helper import command

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


    @command()
    def previousAction(self, request={}):
        self.sioyek.prev_state()

    @command()
    def nextAction(self, request={}):
        self.sioyek.next_state()

    @command()
    def moveLeftAction(self, request={}):
        return 'xdotool getactivewindow  type {repeat}H'

    @command()
    def moveRightAction(self, request={}):
        return 'xdotool getactivewindow  type {repeat}L'

    @command()
    def openAction(self, request):
        self.sioyek.open_prev_doc()

    @command()
    def tabAction(self, request):
        return f'xdotool getactivewindow key Ctrl+o'

    @command()
    def doneAction(self, request):
        self.sioyek.quit()

    @command()
    def fitAction(self, request):
        return f'xdotool getactivewindow key equal'

    @command()
    def hintJumpAction(self, request={}):
        super().showHintAction(request)
        return 'xdotool getactivewindow type v'

    @command()
    def followHintAction(self, request={}):
        slot_names=request['slot_names']
        hint=slot_names.get('text', None)
        print(request)
        if hint:
            hint=hint.strip()
            hint=''.join([h[0] for h in hint.split(' ') if h!=''])
            print(hint)
            return f'xdotool getactivewindow type {hint}'

    @command()
    def createHintAction(self, request={}):
        raise

if __name__=='__main__':
    app=SioyekMode(port=33333)
    app.run()

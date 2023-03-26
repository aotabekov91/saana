import os

from speechToCommand.utils.helper import osAppCommand

from ..vim import VimMode

class RangerMode(VimMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(RangerMode, self).__init__(
                 keyword='ranger', 
                 info='Ranger', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['ranger'])

    @osAppCommand()
    def putAction(self, request={}):
        return 'xdotool getactivewindow type pp' 


if __name__=='__main__':
    app=RangerMode(port=33333)
    app.run()

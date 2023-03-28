import os

from speechToCommand.utils.helper import command
from speechToCommand.utils.moder import GenericMode

class KittyMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(KittyMode, self).__init__(
                 keyword='kitty', 
                 info='Kitty', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=['kitty'])


if __name__=='__main__':
    app=KittyMode(port=33333)
    app.run()

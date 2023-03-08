import sys

from speechToCommand.utils.moder import BaseMode

class GenericMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(GenericMode, self).__init__(
                keyword='generic',
                info='Generic commands',
                port=port,
                parent_port=parent_port,
                config=config
                )

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

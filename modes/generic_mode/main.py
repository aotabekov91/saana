import sys

from speechToCommand.utils.moder import BaseGenericMode

class GenericMode(BaseGenericMode):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 ):

        super(GenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                )
        print(self.port, self.parent_port)

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

import sys

from speechToCommand.utils.moder import BaseMode

class ChangeMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ChangeMode, self).__init__(
                keyword='change',
                info='Change modes',
                port=port,
                parent_port=parent_port,
                config=config
                )

    def changeMode(self, request=None, mode_name=None):
        if not mode_name:
            slotNames=request.get('slot_names')
            mode_name=slotNames.get('mode')
        self.parent_socket.send_json({'command':'setCurrentMode', 'mode_name':mode_name})
        respond=self.parent_socket.recv_json()
        print(respond)

if __name__=='__main__':
    app=ChangeMode(port=33333, parent_port=44444)
    app.run()

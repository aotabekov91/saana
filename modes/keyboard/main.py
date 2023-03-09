import zmq
import subprocess

from speechToCommand.utils.moder import BaseMode

class KeyboardMode(BaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(KeyboardMode, self).__init__(
                keyword='keyboard',
                info='Change keyboard language',
                port=port,
                parent_port=parent_port,
                config=config
                )

    def reset_prev_mode(self):
        self.parent_socket.send_json({'command':'previousMode'})
        prev_mode=self.parent_socket.recv_json().get('previousMode', '')
        if prev_mode!='':
            self.parent_socket.send_json({'command':'setCurrentMode', 'mode_name':prev_mode})
            respond=self.parent_socket.recv_json()
            print(respond)

    @BaseMode.respond
    def changeKeyboard(self, request):
        lan=request['slot_names']['lan']
        subprocess.Popen(['setxkbmap', lan])
        self.reset_prev_mode()

if __name__=='__main__':
    app=KeyboardMode(port=33333, parent_port=44444)
    app.run()

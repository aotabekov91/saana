import zmq
import subprocess

from speechToCommand.utils.moder import Mode

class KeyboardMode(Mode):

    def __init__(self, config):
        super(KeyboardMode, self).__init__(config, keyword='keyboard', info='Keyboard')

    def get_mode(self):
        self.parent_socket.send_json({'command':'previousMode'})
        data=self.parent_socket.recv_json()
        return data['previousMode']

    def set_mode(self, mode):
        self.parent_socket.send_json({'command':'setCurrentMode', 'mode_name':mode})
        print(self.parent_socket.recv_json())

    def handleRequest(self, request):
        if request['command']=='KeyboardMode_changeKeyboard':
            _, __, ___, slots=self.parse_request(request)
            if slots:
                lan=slots[0]['value']['value']
                old_mode=self.get_mode()
                self.changeKeyboard(lan)
                self.set_mode(old_mode)

    def changeKeyboard(self, lan):
        if lan in ['english', 'en']:
            lan='us'
        elif lan in ['german', 'de']:
            lan='de'
        elif lan in ['russian', 'ru']:
            lan='ru'
        elif lan in ['turkish', 'tr']:
            lan='tr'
        subprocess.Popen(['setxkbmap', lan])

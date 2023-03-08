import sys

from speechToCommand.utils.moder import Mode

class ChangeMode(Mode):
    def __init__(self, config):
        super(ChangeMode, self).__init__(config, keyword='changer', info='Change modes')

    def set_mode(self, mode):
        self.parent_socket.send_json({'command':'setCurrentMode', 'mode_keyword':mode})
        print(self.parent_socket.recv_json())

    def handleRequest(self, request):
        print(f'{self.__class__.__name__}: {request}')
        if request['command']=='ChangeMode_changeMode':
            _, __, ___, slots=self.parse_request(request)
            if not slots: return
            mode_name=slots[0]['value']['value']
            self.set_mode(mode_name)

if __name__=='__main__':
    app=ChangeMode({'port':8234})
    app.tlist=app.get_tasks()
    app.ui.addWidgetsToList(app.tlist)
    app.ui.show()
    sys.exit(app.exec_())

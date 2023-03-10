import sys

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class ChangeMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ChangeMode, self).__init__(
                keyword='change',
                info='Change modes',
                port=port,
                parent_port=parent_port,
                config=config
                )
        self.ui=ListMainWindow(self, 'ChangeMode - own_floating', 'Change: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.modes=self.get_modes()

    def get_modes(self):
        self.parent_socket.send_json({'command':'getAllModes'})
        modes=self.parent_socket.recv_json().get('allModes', [])
        items=[]
        for m in modes.values():
            items+=[{'top':m['keyword'], 
                     'down': m['info'],
                     'id':m['mode_name']}]
        return items

    def showAction(self, request={}):
        self.ui.addWidgetsToList(self.modes)
        self.ui.show()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        if not item: return

        mode_name=item.itemData['id']
        self.changeMode(mode_name=mode_name)

        self.ui.edit.clear()
        self.ui.hide()
        

        self.parent_socket.send_json({'command':'setModeAction',
                                      'mode_name':mode_name,
                                      'mode_action':'showAction'
                                      })
        respond=self.parent_socket.recv_json()

        print(respond)


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

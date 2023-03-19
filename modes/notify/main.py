import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets import MessageMainWindow

class NotifyMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(NotifyMode, self).__init__(
                 keyword='notify', 
                 info='Notifier', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.ui =  MessageMainWindow(self, 'Message - own_floating')

    def notifyAction(self, request):

        slot_names=request['slot_names']
        mode_name=slot_names.get('mode_name', self.__class__.__name__)
        text=slot_names.get('text', '')
        detail=slot_names.get('detail', '')
        timeout=slot_names.get('timeout', 5000)

        self.ui.set_title(mode_name)
        self.ui.set_information(text)
        self.ui.set_detail(detail)
        self.ui.set_timer(timeout)
        self.ui.show()

if __name__=='__main__':
    app=NotifyMode(port=33333)
    app.run()

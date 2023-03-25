import sys
import zmq
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .base_mode import BaseMode 
from speechToCommand.utils.widgets.qapplication import QBaseApplication 

class QBaseMode(BaseMode, QBaseApplication):

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 window_classes=[],
                 argv=[],
                 app_name='own_floating'):

        super(QBaseMode, self).__init__(
                 keyword=keyword, 
                 info=info, 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 argv=argv,
                 app_name=app_name)

    def run(self):
        sys.exit(self.exec_())
        print(f'{self.__class__.__name__}: exiting')

    def exit(self, request={}):
        self.running=False
        self.zeromq_listener.running=False
        sys.exit()

if __name__=='__main__':
    app=QBaseMode(port=33333, parent_port=44444)
    app.run()

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
                 argv=[]):

        super(QBaseMode, self).__init__(
                 keyword=keyword, 
                 info=info, 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 argv=argv)

    def run(self):
        sys.exit(self.exec_())

    def exit(self, request={}):
        self.zeromq_listener.wait=False
        self.zeromq_listener.running=False
        if self.ui: self.ui.close()
        self.close()

if __name__=='__main__':
    app=QBaseMode(port=33333, parent_port=44444)
    app.run()

import os
import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import ZMQListener
from speechToCommand.utils.window import BaseGenericMode 
from speechToCommand.utils.helper import osGenericCommand

class QBaseGenericMode(BaseGenericMode, QApplication):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 window_classes=[],
                 argv=[],
                 ):
                 
        super(QBaseGenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                argv=argv,
                )

        self.setApplicationName('own_floating')
        self.set_listener()

    def set_listener(self):
        self.listener = QThread()
        self.zeromq_listener=ZMQListener(self)
        self.zeromq_listener.moveToThread(self.listener)
        self.listener.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.request.connect(self.handle_request)
        QTimer.singleShot(0, self.listener.start)

    def run(self):
        sys.exit(self.exec_())

    def exit(self, request={}):
        self.zeromq_listener.wait=False
        self.zeromq_listener.running=False
        if self.ui: self.ui.close()
        self.close()
        
if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

import sys
import zmq
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder.base import BaseMode 

class ZMQListener(QObject):

    request = pyqtSignal(dict)

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent=parent
        self.running = True

    def loop(self):
        while self.running:
            request = self.parent.socket.recv_json()
            self.request.emit(request)

class QBaseMode(BaseMode, QApplication):

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 argv=[]):

        super(QBaseMode, self).__init__(
                 keyword=keyword, 
                 info=info, 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 argv=argv)

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

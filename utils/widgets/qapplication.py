import sys
import zmq
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

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

class QBaseApplication(QApplication):

    def __init__(self, argv=[], app_name='own_floating'):

        super(QBaseApplication, self).__init__(argv)

        self.setApplicationName(app_name)
        self.set_listener()

    def set_listener(self):
        self.listener = QThread()
        self.zeromq_listener=ZMQListener(self)
        self.zeromq_listener.moveToThread(self.listener)
        self.listener.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.request.connect(self.handle_request)
        QTimer.singleShot(0, self.listener.start)

import sys
import zmq
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder.base import BaseMode 

class ZMQListener(QObject):

    request = pyqtSignal(dict)
    reset_socket=pyqtSignal()

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent=parent
        self.running = True
        self.wait=False

    def loop(self):
        while self.running:
            try:
                request = self.parent.socket.recv_json()
                self.request.emit(request)
                self.wait=True
                while self.wait:
                    print(f'{self.parent.__class__.__name__}: waiting')
                    time.sleep(2)
            except zmq.error.ZMQError:
                self.reset_socket.emit()

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
        self.zeromq_listener.reset_socket.connect(self.reset_socket)
        QTimer.singleShot(0, self.listener.start)

    def stop_waiting(self):
        self.zeromq_listener.wait=False

    def reset_socket(self):
        self.parent.socket.send_json(
                {'status':'nok', 'info': f'error in {self.__class__.__name__}'}
                )
        self.stop_waiting()

    def run(self):
        sys.exit(self.exec_())

    def exit(self):
        self.zeromq_listener.wait=False
        self.zeromq_listener.running=False
        super().exit()

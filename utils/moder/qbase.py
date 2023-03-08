import zmq
import sys
import time
import threading

from configparser import ConfigParser
from speechToCommand.utils.moder import BaseMode 

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ZMQListener(QObject):

    request=pyqtSignal(dict)

    def __init__(self, parent):
        super(ZMQListener, self).__init__()
        self.parent=parent
        self.port=parent.port
        self.running=True

    def loop(self):
        while self.running:
            request=self.parent.socket.recv_json()
            self.request.emit(request)
            self.parent.socket.send_json({'status': f'{self.parent.__class__.__name__} received request'})

class QBaseMode(BaseMode, QApplication):

    def __init__(self, keyword='', info=None, config=None):
        super(QBaseMode, self).__init__(keyword, info, config, [])
        self.setApplicationName('own_floating')
        self.set_listener()

    def set_listener(self):
        self.listener_thread = QThread()
        self.listener=ZMQListener(self)
        self.listener.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.listener.loop)
        self.listener.request.connect(self.handle_request)
        QTimer.singleShot(0, self.listener_thread.start)

    def _run(self):
        sys.exit(self.exec_())

    def exit(self):
        self.listener.running=False
        super().exit()

if __name__=='__main__':
    config=ConfigParser()
    config.read({'Custom':{'port':8001}})
    app=BaseMode(config=config)
    app.run()

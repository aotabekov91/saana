import os
import zmq
import json
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ZeroMQ_TCPListener(QObject):
    request = pyqtSignal(dict)
    def __init__(self, parent):
        super(ZeroMQ_TCPListener, self).__init__()
        self.parent=parent
        self.port=parent.port
        self.createConnection()
    
    def createConnection(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f'tcp://*:{self.port}')
        self.running = True
    
    def loop(self):
        while self.running:
            request = self.socket.recv_json()
            mode_name=f'{self.parent.__class__.__name__}'
            self.socket.send_json({'status': f'{mode_name} received request'})
            self.request.emit(request)

class Mode(QApplication):

    def __init__(self, config, keyword='', info='', ui=None):
        super(Mode, self).__init__([])
        self.setApplicationName('own_floating')
        self.config=config
        self.ui=ui
        self.info=info
        self.keyword=keyword

        self.set_info()
        self.set_keyword()

        self.set_port()
        self.connect_to_parent()

    def connect_to_parent(self):
        if self.config.get('parent_port'):
            context=zmq.Context()
            self.parent_socket=context.socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.config["parent_port"]}')
            self.parent_socket.send_json({'command':'registerModeKeyword', 
                                          'mode_name':self.__class__.__name__, 
                                          'keyword':self.keyword})
            print(self.parent_socket.recv_json())

    def set_info(self):
        if hasattr(self.config, 'info'):
            self.info=self.config.get('info')

    def set_keyword(self):
        if hasattr(self.config, 'keyword'):
            self.keyword=self.config.get('keyword')

    def set_port(self):
        if self.config.get('port'):
            self.port=int(self.config.get('port'))
            self.set_socket()

    def set_socket(self):
        self.listenThread = QThread()
        self.zeromq_listener=ZeroMQ_TCPListener(self)
        self.zeromq_listener.moveToThread(self.listenThread)
        self.listenThread.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.request.connect(self.handleRequest)
        QTimer.singleShot(0, self.listenThread.start)

    def handleRequest(self, request):
        if self.ui: self.ui.handleRequest(request)

    def get_info(self):
        return self.info
        
    def get_keyword(self):
        return self.keyword

    def parse_request(self, request):
        command=request['command']
        input_, intent, slots=(None,)*3
        intent_data=request.get('intent_data')
        if not intent_data:
            return command, input_, intent, slots
        else:
            input_=intent_data['input']
            intent=intent_data['intent']
            slots=intent_data['slots']
            if len(slots)==0: slots=None
            return command, input_, intent, slots

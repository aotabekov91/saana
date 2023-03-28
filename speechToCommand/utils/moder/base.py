import os
import sys
import zmq
import time
import inspect

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import asyncio
from i3ipc.aio import Connection

from os.path import abspath
from configparser import ConfigParser

from ..helper import ZMQListener 

class BaseMode(QApplication):

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 window_classes='all',
                 app_name='own_floating'):

        super(BaseMode, self).__init__([])

        self.info=info
        self.port=port
        self.config=config
        self.running = False
        self.keyword=keyword
        self.intents_path=None
        self.parent_port=parent_port

        self.setApplicationName(app_name)

        self.window_classes=window_classes
        self.manager=asyncio.run(Connection().connect())

        self.set_config()
        self.set_intents_path()
        self.set_connection()
        self.set_listener()

        self.register_mode()

    def set_config(self):
        if self.info is None: self.info=self.__class__.__name__
        if self.config is None:
            file_path=os.path.abspath(inspect.getfile(self.__class__))
            mode_path=os.path.dirname(file_path).replace('\\', '/')
            config_path=f'{mode_path}/config.ini'
            if os.path.isfile(config_path):
                self.config=ConfigParser()
                self.config.read(config_path)
            else:
                self.config=ConfigParser()
        if self.config.has_section('Custom'):
            if self.config.has_option('Custom', 'info'):
                self.info=self.config.get('Custom', 'info')
            if self.config.has_option('Custom', 'keyword'):
                self.keyword=self.config.get('Custom', 'keyword')
            if self.config.has_option('Custom', 'port'):
                self.port=self.config.getint('Custom', 'port')
            if self.config.has_option('Custom', 'window_classes'):
                self.window_classes=self.config.getint('Custom', 'window_classes')

    def set_intents_path(self):
        file_path=os.path.abspath(inspect.getfile(self.__class__))
        main_path=os.path.dirname(file_path).replace('\\', '/')
        path=f'{main_path}/intents.yaml'
        if os.path.isfile(path): self.intents_path=path

    def register_mode(self):
        if self.parent_port:
            poller=zmq.Poller()
            poller.register(self.parent_socket, flags=zmq.POLLIN)

            self.parent_socket.send_json({
                'command': 'registerMode',
                'mode_name':self.__class__.__name__,
                'keyword':self.keyword,
                'info': self.info,
                'port': self.port,
                'window_classes': self.window_classes,
                'intents_path': self.intents_path})

            sock=poller.poll(timeout=1000)
            if len(sock)>0 and sock[0][0]==self.parent_socket:
                respond=self.parent_socket.recv_json(zmq.NOBLOCK)
            poller.unregister(self.parent_socket)

    def handle_request(self, request):
        command=request['command'].rsplit('_', 1)
        mode_name, action=command[0], command[-1]
        mode_func=getattr(self, action, False)


        ui_func=None
        if hasattr(self, 'ui'):
            ui_func=getattr(self.ui, action, None)

        try:

            msg=None
            if mode_func:
                mode_func(request)
                msg=f"{self.__class__.__name__}: handled request"
            elif ui_func and (self.ui.isVisible() or 'showAction' in action):
                ui_func(request)
                msg=f"{self.__class__.__name__}: UI handled request"
            elif self.__class__.__name__!=mode_name:
                if self.parent_port:
                    self.parent_socket.send_json(
                            {'command':'setModeAction',
                             'mode_name':mode_name,
                             'mode_action': request['command'],
                             'slot_names': request['slot_names'],
                             'intent_data': request['intent_data'],
                             'own_only': True})
                    respond=self.parent_socket.recv_json()
                    msg=f'{self.__class__.__name__}: {mode_name} {request["command"]} {request["slot_names"]}'
                else:
                    msg=f'{self.__class__.__name__}: not understood'

        except:
            err_type, error, traceback = sys.exc_info()
            msg='{err}'.format(err=error)
        print(msg)

    def set_connection(self):
        if self.parent_port:
            self.parent_socket=zmq.Context().socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.parent_port}')
        try:
            self.socket = zmq.Context().socket(zmq.PULL)
            if self.port:
                self.socket.bind(f'tcp://*:{self.port}')
            else:
                self.port=self.socket.bind_to_random_port('tcp://*')
            self.set_listener()
        except:
            if self.parent_port:
                socket = zmq.Context().socket(zmq.PUSH)
                socket.connect(f'tcp://localhost:{self.port}')
                socket.send_json({'command':'setParentPortAction',
                                  'slot_names':{'parent_port':self.parent_port}})
                self.register_mode()
            sys.exit()

    def set_listener(self):
        self.listener = QThread()
        self.zeromq_listener=ZMQListener(self)
        self.zeromq_listener.moveToThread(self.listener)
        self.listener.started.connect(self.zeromq_listener.loop)
        self.zeromq_listener.request.connect(self.handle_request)
        QTimer.singleShot(0, self.listener.start)

    def get_mode_folder(self):
        file_path=os.path.abspath(inspect.getfile(self.__class__))
        return os.path.dirname(file_path).replace('\\', '/')

    def run(self):
        self.running=True
        sys.exit(self.exec_())

    def exit(self, request={}):
        self.running=False
        self.close()
        print(f'{self.__class__.__name__}: exiting')
        sys.exit()

if __name__=='__main__':
    app=BaseMode(port=33333, parent_port=44444)
    app.run()

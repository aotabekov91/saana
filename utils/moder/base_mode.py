import os
import sys
import zmq
import inspect

import asyncio
from i3ipc.aio import Connection

from os.path import abspath
from configparser import ConfigParser

class BaseMode:

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 window_classes='all',
                 argv=None,
                 app_name='own_floating'):

        if type(argv)==list:
            super(BaseMode, self).__init__(argv, app_name)
        else:
            super(BaseMode, self).__init__()

        self.ui=None

        self.info=info
        self.port=port
        self.config=config
        self.keyword=keyword
        self.intents_path=None
        self.parent_port=parent_port

        self.window_classes=window_classes
        self.manager=asyncio.run(Connection().connect())

        self.locked=False
        self.running = False

        self.set_config()
        self.set_intents_path()
        self.set_connection()
        self.register()
        # print(self.__class__.__name__, self.port, self.parent_port)

    def lockAction(self, request):
        self.locked=True

    def unlockAction(self, request):
        self.locked=False

    def get_current_window(self):
        tree=asyncio.run(self.manager.get_tree())
        return tree.find_focused()

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

    def register(self, request=None):
        success=False

        if self.parent_port:

            poller=zmq.Poller()
            poller.register(self.parent_socket, flags=zmq.POLLOUT)

            if poller.poll(timeout=50):

                self.parent_socket.send_json({
                    'command': 'registerMode',
                    'mode_name':self.__class__.__name__,
                    'keyword':self.keyword,
                    'info': self.info,
                    'port': self.port,
                    'window_classes': self.window_classes,
                    'intents_path': self.intents_path})

                respond=self.parent_socket.recv_json()
                # print(f'Handler responded with: {respond}')
                success=True
            poller.unregister(self.parent_socket)

        if request: 

            self.socket.send_json({'registered':success})

    def handle_request(self, request):
        # print(f'{self.__class__.__name__} received request: {request}')
        command=request['command'].rsplit('_', 1)
        mode_name, action=command[0], command[-1]
        mode_func=getattr(self, action, False)
        ui_func=None
        if hasattr(self, 'ui'):
            ui_func=getattr(self.ui, action, False)

        try:
            msg=None
            if mode_func:
                mode_func(request)
                msg={"status":f"{self.__class__.__name__} handled request"}
            elif ui_func and (self.ui.isVisible() or 'showAction' in action):
                ui_func(request)
                msg={"status":f"{self.__class__.__name__}'s UI handled request"}

            elif self.__class__.__name__!=mode_name and not self.locked:
                if self.parent_port:
                    self.parent_socket.send_json(
                            {'command':'setModeAction',
                             'mode_name':mode_name,
                             'mode_action': request['command'],
                             'slot_names': request['slot_names'],
                             'intent_data': request['intent_data'],
                             'own_only': True})
                    respond=self.parent_socket.recv_json()

                else:
                    msg={"status":"not understood"}
        except:
            err_type, error, traceback = sys.exc_info()
            msg='{err}'.format(err=error)

        # print(msg)

    def setParentPortAction(self, request={}):
        slot_names=request['slot_names']
        parent_port=slot_names.get('parent_port', None)
        if parent_port:
            self.parent_port=parent_port
            self.parent_socket=zmq.Context().socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.parent_port}')

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
        except:
            # print(f'{self.__class__.__name__} is already running')
            if self.parent_port:
                socket = zmq.Context().socket(zmq.PUSH)
                socket.connect(f'tcp://localhost:{self.port}')
                socket.send_json({'command':'setParentPortAction',
                                  'slot_names':{'parent_port':self.parent_port}})
                self.register()
            sys.exit()

    def get_mode_folder(self):
        file_path=os.path.abspath(inspect.getfile(self.__class__))
        return os.path.dirname(file_path).replace('\\', '/')

    def run(self):
        self.running=True
        while self.running:
            request = self.socket.recv_json()
            self.handle_request(request)
        print(f'{self.__class__.__name__}: exiting')

    def exit(self, request=None):
        # print(self.__class__.__name__, 'exiting')
        self.running=False

if __name__=='__main__':
    app=BaseMode(port=33333, parent_port=44444)
    app.run()

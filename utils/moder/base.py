import os
import sys
import zmq
import time
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
                 window_classes=[],
                 argv=None):
        if type(argv)==list:
            super(BaseMode, self).__init__(argv)
        else:
            super(BaseMode, self).__init__()

        self.ui=None
        self.current_window=None
        self.manager=asyncio.run(Connection().connect())

        self.info=info
        self.port=port
        self.config=config
        self.keyword=keyword
        self.window_classes=window_classes
        self.intents_path=None
        self.parent_port=parent_port

        self.running = False

        self.set_config()
        self.set_intents_path()
        self.set_connection()

        self.register()

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
                print(f'Handler responded with: {respond}')
                success=True
            poller.unregister(self.parent_socket)

        if request: 

            self.socket.send_json({'registered':success})

    def handle_request(self, request):
        print(f'{self.__class__.__name__} received request: {request}')
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
            check_respond=self.checkAction(request)
            if not msg and not request['own_only'] and check_respond:
                mode_names=check_respond.get('mode_names', [])
                mode_name=self.__class__.__name__
                mode_names.pop(mode_name.index(mode_name))
                msg={"status":f"{self.__class__.__name__}: Sending to other modes"} 
                if len(mode_names)>0:
                    for mode_name in mode_names:
                        msg={"status":f"{self.__class__.__name__}: Sending to {mode_name}"}
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

        print(msg)

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.PULL)
        if self.port:
            self.socket.bind(f'tcp://*:{self.port}')
        else:
            self.port=self.socket.bind_to_random_port('tcp://*')
        if self.parent_port:
            self.parent_socket=zmq.Context().socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.parent_port}')

    def get_current_window(self):
        tree=asyncio.run(self.manager.get_tree())
        window=tree.find_focused()
        return getattr(window, 'window_class', None)

    def set_current_window(self):
        tree=asyncio.run(self.manager.get_tree())
        self.current_window=tree.find_focused()

    def checkAction(self, request):
        window_class=self.get_current_window()
        if window_class and self.parent_port:
            self.parent_socket.send_json(
                    {'command':'setCurrentWindow',
                     'window_class':window_class})
            return self.parent_socket.recv_json()

    def run(self):
        self.running=True
        while self.running:
            request = self.socket.recv_json()
            self.handle_request(request)

    def exit(self, request=None):
        self.running=False
        if request:
            self.socket.send_json({'status':'exiting'})

if __name__=='__main__':
    app=BaseMode(port=33333, parent_port=44444)
    app.run()

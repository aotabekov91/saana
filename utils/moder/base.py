import os
import sys
import zmq
import time
import inspect

from inspect import getsourcefile
from os.path import abspath

from configparser import ConfigParser

class BaseMode:

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 argv=None):
        if type(argv)==list:
            super(BaseMode, self).__init__(argv)
        else:
            super(BaseMode, self).__init__()

        self.ui=None
        self.info=info
        self.port=port
        self.config=config
        self.keyword=keyword
        self.intents_path=None
        self.parent_port=parent_port

        self.running = False

        self.set_config()
        self.set_intents_path()
        self.set_connection()

        self.register()

    def get_folder(self):
        file_path=os.path.abspath(inspect.getfile(self.__class__))
        return os.path.dirname(file_path).replace('\\', '/')

    def set_intents_path(self):
        main_path=self.get_folder()

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
                    'intents_path': self.intents_path})

                respond=self.parent_socket.recv_json()
                print(f'Handler responded with: {respond}')
                success=True
            poller.unregister(self.parent_socket)

        if request: 

            self.socket.send_json({'registered':success})

    def handle_request(self, request):
        print(f'{self.__class__.__name__} received request: {request}')
        command=request['command'].split('_')
        mode_name, action=command[0], command[-1]

        func=getattr(self, action, False)
        try:
            if func:
                func(request)
                msg={"status":f"{self.__class__.__name__} handled request"}
            elif self.ui and (self.ui.isVisible() or 'showAction' in action):
                self.ui.handle_request(request)
                msg={"status":f"{self.__class__.__name__}'s UI handled request"}
            else:
                msg={"status":"not understood"}

        except:
            err_type, error, traceback = sys.exc_info()
            msg='{err}'.format(err=error)

        print(msg)
        self.stop_waiting()

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

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.PULL)
        if self.port:
            self.socket.bind(f'tcp://*:{self.port}')
        else:
            self.port=self.socket.bind_to_random_port('tcp://*')
        if self.parent_port:
            self.parent_socket=zmq.Context().socket(zmq.REQ)
            self.parent_socket.connect(f'tcp://localhost:{self.parent_port}')


    def run(self):
        self.running=True
        while self.running:
            request = self.socket.recv_json()
            self.handle_request(request)

    def exit(self, request=None):
        self.running=False
        if request:
            self.socket.send_json({'status':'exiting'})

    def stop_waiting(self):
        pass
    
    def respond(func):
        def inner(self, request):
            try:
                func(self, request)
                msg='{name}: Success'.format(name=func.__name__)
            except:
                err_type, error, traceback = sys.exc_info()
                msg='{name}: {err}'.format(name=func.__name__, err=error)
            if request!=None and len(request)>0:
                self.socket.send_json({'status':msg})
                self.stop_waiting()
        return inner

if __name__=='__main__':
    app=BaseMode(port=33333, parent_port=44444)
    app.run()

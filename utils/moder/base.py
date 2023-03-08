import os
import zmq
import time

from configparser import ConfigParser

class BaseMode:

    def __init__(self, 
                 keyword=None, 
                 info=None, 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 *args, **kwargs):
        super(BaseMode, self).__init__(*args, **kwargs)

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

    def set_intents_path(self):
        main_path=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        path=f'{main_path}/intents.yaml'
        if os.path.isfile(path): self.intents_path=path

    def register(self, request=None):
        success=False

        if self.parent_port:

            poller=zmq.Poller()
            poller.register(self.parent_socket, flags=zmq.POLLOUT)

            if poller.poll(timeout=500):

                self.parent_socket.send_json({
                    'mode_name':self.__class__.__name__,
                    'keyword':self.keyword,
                    'info': self.info,
                    'port': self.port,
                    'intents_path': self.intents_path})

                print(self.parent_socket.recv_json())
                success=True
            poller.unregister(self.parent_socket)

        if request: 

            self.socket.send_json({'registered':success})

    def handle_request(self, request):
        print(f'{self.__class__.__name__} received request: {request}')
        command=request['command'].split('_')
        mode_name, action=command[0], command[-1]

        func=getattr(self, action, False)
        # try:

        if func:
            func(request)
        elif self.ui:
            self.ui.handle_request(request, self.socket)
        else:
            self.socket.send_json({"status":"request not understood"})

        # except:
        #     self.socket.send_json({"status":"error occurred"})

    def set_config(self):
        if self.info is None: self.info=self.__class__.__name__
        if self.config is None:
            mode_path=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
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

        self.socket = zmq.Context().socket(zmq.REP)
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
        if request: self.socket.send_json({'status':'exiting'})

if __name__=='__main__':
    app=BaseMode(port=33333, parent_port=44444)
    app.run()

import os
import zmq
import threading

from configparser import ConfigParser

from speechToCommand.utils.handler import Handler
from speechToCommand.utils.intender import Intender
from speechToCommand.utils.listener import Listener

class SpeechToCommand:
    def __init__(self,
                 config=None,
                 handler_port=None,
                 listener_port=None,
                 intender_port=None):

        self.config=config

        self.handler_port=handler_port
        self.listener_port=listener_port
        self.intender_port=intender_port

        self.set_config()
        self.set_connection()

        self.intender=Intender(self)
        self.listener=Listener(self)

        self.handler=Handler(self)

    def set_config(self):

        if not self.config:
            main_path=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
            config_path=f'{main_path}/config.ini'
            if os.path.isfile(config_path):
                self.config=ConfigParser()
                self.config.read(config_path)
            else:
                self.config=ConfigParser()

        if self.config.has_section('General'):
            if not self.handler_port:
                if self.config.has_option('General', 'handler_port'):
                    self.handler_port=self.config.getint('General', 'handler_port')
            if not self.listener_port:
                if self.config.has_option('General', 'listener_port'):
                    self.listener_port=self.config.getint('General', 'listener_port')
            if not self.intender_port:
                if self.config.has_option('General', 'intender_port'):
                    self.listener_port=self.config.getint('General', 'listener_port')
               
    def set_connection(self):
        self.handler_socket = zmq.Context().socket(zmq.REP)
        if self.handler_port:
            self.handler_socket.bind(f'tcp://*:{self.handler_port}')
        else:
            self.handler_port=self.handler_socket.bind_to_random_port('tcp://*')

        self.listener_socket = zmq.Context().socket(zmq.PULL)
        if self.listener_port:
            self.listener_socket.connect(f'tcp://localhost:{self.listener_port}')

        self.intender_socket = zmq.Context().socket(zmq.REQ)
        if self.intender_port:
            self.intender_socket.connect(f'tcp://*:{self.intender_port}')

    def run(self):
        self.handler.handle()

    def exit(self):
        self.listener.exit()
        self.handler.exit()

if __name__ == '__main__':
    r=SpeechToCommand()
    r.run()

import os
import sys
import zmq
import threading
import argparse

from configparser import ConfigParser

from speechToCommand.utils.handler import Handler
from speechToCommand.utils.listener import Listener

from speechToCommand.utils.intender import get_intender

from tendo import singleton

class SpeechToCommand:
    def __init__(self,
                 config=None,
                 handler_port=None,
                 listener_port=None,
                 intender_port_1=None,
                 intender_port_2=None,
                 intender_port_3=None,
                 ):

        self.config=config

        self.handler_port=handler_port
        self.listener_port=listener_port
        self.intender_port_1=intender_port_1
        self.intender_port_2=intender_port_2
        self.intender_port_3=intender_port_3

        self.set_config()
        self.set_connection()
        self.set_intenders()

        self.handler=Handler(self)

    def set_listener(self):
        self.listener=Listener(self)

    def set_intenders(self):

        self.intender_1=get_intender(self.intender_port_1)
        self.intender_2=get_intender(self.intender_port_2)
        self.intender_3=get_intender(self.intender_port_3)

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
            if not self.intender_port_1:
                if self.config.has_option('General', 'intender_port_1'):
                    self.intender_port_1=self.config.getint('General', 'intender_port_1')
            if not self.intender_port_2:
                if self.config.has_option('General', 'intender_port_2'):
                    self.intender_port_2=self.config.getint('General', 'intender_port_2')
            if not self.intender_port_3:
                if self.config.has_option('General', 'intender_port_3'):
                    self.intender_port_3=self.config.getint('General', 'intender_port_3')
               
    def set_connection(self):
        self.handler_socket = zmq.Context().socket(zmq.REP)
        if self.handler_port:
            self.handler_socket.bind(f'tcp://*:{self.handler_port}')
        else:
            self.handler_port=self.handler_socket.bind_to_random_port('tcp://*')

        self.listener_socket = zmq.Context().socket(zmq.PULL)
        if self.listener_port:
            self.listener_socket.connect(f'tcp://localhost:{self.listener_port}')

        self.intender_socket_1 = zmq.Context().socket(zmq.REQ)
        if self.intender_port_1:
            self.intender_socket_1.connect(f'tcp://localhost:{self.intender_port_1}')

        self.intender_socket_2 = zmq.Context().socket(zmq.REQ)
        if self.intender_port_2:
            self.intender_socket_2.connect(f'tcp://localhost:{self.intender_port_2}')

        self.intender_socket_3 = zmq.Context().socket(zmq.REQ)
        if self.intender_port_3:
            self.intender_socket_3.connect(f'tcp://localhost:{self.intender_port_3}')

    def run(self):
        self.handler.handle()

    def exit(self):
        self.listener.exit()
        self.handler.exit()
        for i in range(1, 4):
            intender=getattr(self, f'intender_socket_{i}')
            intender.send_json({'command':'exit'})
            print(intender.recv_json())

if __name__ == '__main__':

    try:

        me=singleton.SingleInstance()

        parser=argparse.ArgumentParser()
        parser.add_argument('--listener', nargs='?', type=bool, default=True)
        args=parser.parse_args()
        r=SpeechToCommand()
        if args.listener:
            r.set_listener()
        r.run()

    except singleton.SingleInstanceException:

        print('An instance of SpeechToCommand is already running!')
        sys.exit()

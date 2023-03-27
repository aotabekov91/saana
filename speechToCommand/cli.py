#!/usr/lib/python
import os
import zmq
import threading
import argparse

from configparser import ConfigParser

class SpeechToCommandCLI:
    def __init__(self, config=None, handler_port=None):

        self.config=config
        self.handler_port=handler_port

        self.set_config()
        self.set_connection()
        self.set_argparser()
        self.poller=zmq.Poller()

    def set_argparser(self):

        self.parser=argparse.ArgumentParser()
        self.parser.add_argument('-m', '--modes', action='append')
        self.parser.add_argument('-p', '--port', type=int)
        self.parser.add_argument('-a', '--all', action='append')

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

    def set_connection(self):
        self.handler_socket = zmq.Context().socket(zmq.REQ)
        if self.handler_port:
            self.handler_socket.connect(f'tcp://localhost:{self.handler_port}')

    def set_mode_connection(self, port):
        socket = zmq.Context().socket(zmq.PUSH)
        socket.connect(f'tcp://localhost:{port}')
        return socket

    def run_mode_actions_directly(self, actions, port):
        socket=self.set_mode_connection(port)
        for mode_action in actions:
            socket.send_json({'command': mode_action})

    def run_mode_actions_via_parent(self, actions):
        if self.handler_port:
            for mode_action in actions:
                tmp=mode_action.split('_')
                mode_name, action_name=tmp[0], tmp[-1]

                try:
                    self.handler_socket.send_json({
                            'command':'setModeAction',
                            'mode_name':mode_name,
                            'mode_action': mode_action,
                            })
                    print(self.handler_socket.recv_json())
                except:
                    pass


    def run_handler_actions(self, actions):
        if self.handler_port:
            for action in actions:

                try:

                    self.handler_socket.send_json({'command':action})
                    print(self.handler_socket.recv_json())

                except:
                    pass



    def run(self):
        args=self.parser.parse_args()
        if args.modes and args.port:
            self.run_mode_actions_directly(args.modes, args.port)
        elif args.modes:
            self.run_mode_actions_via_parent(args.modes)
        elif args.all:
            self.run_handler_actions(args.all)

if __name__ == '__main__':
    r=SpeechToCommandCLI()
    r.run()
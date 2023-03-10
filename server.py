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

    def set_argparser(self):

        self.parser=argparse.ArgumentParser()
        self.parser.add_argument('-a', '--actions', action='append')


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

    def run_mode_actions(self, actions):
        if self.handler_port:

            for action in actions:
                tmp=action.split('_')
                mode_name, mode_action=tmp[0], tmp[-1]

                self.handler_socket.send_json({
                        'command':'setModeAction',
                        'mode_name':mode_name,
                        'mode_action':mode_action
                        })

                print(self.handler_socket.recv_json())

    def run(self):

        args=self.parser.parse_args()
        if args.actions:
            self.run_mode_actions(args.actions)

if __name__ == '__main__':
    r=SpeechToCommandCLI()
    r.run()

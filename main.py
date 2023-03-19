import os
import sys
import zmq
import inspect
import threading
import argparse

from configparser import ConfigParser

from speechToCommand.utils.handler import Handler

from tendo import singleton

class SpeechToCommand:
    def __init__(self, config=None):

        self.config=config
        self.set_config()
        self.handler=Handler(self.config)

    def set_config(self):

        if not self.config:
            main_path=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
            config_path=f'{main_path}/config.ini'
            if os.path.isfile(config_path):
                self.config=ConfigParser()
                self.config.read(config_path)
            else:
                self.config=ConfigParser()
               
    def run(self):
        self.handler.run()

    def exit(self):
        self.handler.exit()

if __name__ == '__main__':

    try:

        me=singleton.SingleInstance()
        app=SpeechToCommand()
        app.run()

    except singleton.SingleInstanceException:

        print('An instance of SpeechToCommand is already running!')
        sys.exit()

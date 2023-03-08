import zmq
import json
import threading
import configparser

from speechToCommand.utils.loader import Loader
from speechToCommand.utils.reporter import Reporter
from speechToCommand.utils.intender import Intender
from speechToCommand.utils.listener import Listener

class SpeechToCommand:
    def __init__(self, config_path='/home/adam/bin/python/speechToCommand/config.ini'):

        self.currentMode=None
        self.previousMode=None
        self.keyword_to_mode_names={}
        self.modes={}
        self.load_configs(config_path)
        self.set_modules()
        self.set_connect()

    def load_configs(self, config_path):
        self.config=configparser.ConfigParser()
        self.config.read(config_path)

    def set_modules(self):

        self.reporter=Reporter(self)
        self.loader=Loader(self.config)
        self.modes=self.loader.load_modes()
        self.intender=Intender(self.modes)
        self.listener=Listener(self.config['Listener'])

    def set_connect(self):
        context=zmq.Context()
        self.listenSocket=context.socket(zmq.PULL)
        self.listenSocket.connect(f'tcp://localhost:{self.listener.port}')

    def setCurrentMode(self, mode_name):
        self.previousMode=self.currentMode
        self.currentMode=mode_name

    def act(self, mode_name, intent_name, intent_data):
        def send_action(port, action, data):
            context=zmq.Context()
            socket=context.socket(zmq.REQ)
            socket.connect(f'tcp://localhost:{port}')
            socket.send_json({'command':action, 'intent_data':data})
            respond=socket.recv_json()
            print(respond)

        if mode_name and mode_name in self.modes:
            mode_class, port=self.modes[mode_name]
        elif self.currentMode and self.currentMode in self.modes:
            mode_class, port=self.modes[self.currentMode]
        else:
            return

        t=threading.Thread(target=send_action, args=(port, intent_name, intent_data))
        t.setDaemon(True)
        t.start()

    def activate(self):
        while True:

            data=self.listenSocket.recv_json()
            
            m_name=None
            if self.currentMode != None:
                m_name, i_name, i_data = self.intender.parse(data['text'], self.currentMode)
                if m_name is None:
                    m_name, i_name, i_data = self.intender.parse(data['text'], 'ChangeMode')
                if m_name is None:
                    m_name, i_name, i_data = self.intender.parse(data['text'], 'GenericMode')
                    if m_name == 'GenericMode': m_name=self.currentMode

            if self.currentMode is None or m_name is None:
                m_name, i_name, i_data = self.intender.parse(data['text'])

            print('Intender: ', m_name, i_name, i_data)

            # if m_name=='GenericMode' and self.currentMode is None: continue

            if m_name:
                self.setCurrentMode(m_name)
                self.act(m_name, i_name, i_data)

if __name__ == '__main__':
    r=SpeechToCommand()
    r.activate()

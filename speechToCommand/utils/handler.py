import sys
import zmq

import threading

import asyncio
from i3ipc.aio import Connection

from configparser import ConfigParser

from multiprocessing import Process

from .listener import Listener
from .intender import Intender
from .interpreter import Interpreter

class Handler:
    def __init__(self, config=ConfigParser(),
                 handler_port=None,
                 intender_port=None,
                 listener_port=None,
                 ):

        self.modes={}
        self.mode_store_data={}
        self.sockets={}

        self.running=True
        self.modes_path=None
        self.current_mode=None
        self.previous_mode=None
        self.last_command=None
        self.last_speech=None
        self.private_mode=False

        self.manager=asyncio.run(Connection().connect())

        self.config=config

        self.port=handler_port
        self.interpreter=Interpreter()
        self.intender_port=intender_port 
        self.listener_port=listener_port 

        self.set_config()
        self.set_connection()

        self.lode_modules()
        self.listen()

    def set_current_mode(self, mode_name):
        self.previous_mode=self.current_mode
        self.current_mode=mode_name

    def set_config(self):
        if self.config.has_section('General'):
            if self.config.has_option('General', 'modes_path'):
                self.modes_path=self.config.get('General', 'modes_path')
            if not self.port:
                if self.config.has_option('General', 'handler_port'):
                    self.port=self.config.getint('General', 'handler_port')
                else:
                    random_socket = zmq.Context().socket(zmq.PUSH)
                    self.port=random_socket.bind_to_random_port(f'tcp://*')
                    random_socket.close()
            if not self.listener_port:
                if self.config.has_option('General', 'listener_port'):
                    self.listener_port=self.config.getint('General', 'listener_port')
                else:
                    random_socket = zmq.Context().socket(zmq.PUSH)
                    self.listener_port=random_socket.bind_to_random_port(f'tcp://*')
                    random_socket.close()
            if not self.intender_port:
                if self.config.has_option('General', 'intender_port'):
                    self.intender_port=self.config.getint('General', 'intender_port')
                else:
                    random_socket = zmq.Context().socket(zmq.PUSH)
                    self.intender_port=random_socket.bind_to_random_port(f'tcp://*')
                    random_socket.close()

    def set_connection(self):
        if self.port:
            self.socket = zmq.Context().socket(zmq.REP)
            self.socket.bind(f'tcp://*:{self.port}')
            self.listener_socket = zmq.Context().socket(zmq.PULL)
            self.listener_socket.connect(f'tcp://localhost:{self.listener_port}')
            self.intender_socket= zmq.Context().socket(zmq.REQ)
            self.intender_socket.connect(f'tcp://localhost:{self.intender_port}')

    def set_current_window(self):

        tree=asyncio.run(self.manager.get_tree())
        window=tree.find_focused()
        window_class=getattr(window, 'window_class', None)

        if window_class is None: return

        mode_names=[]
        modes=[]
        for mode_name, mode_data in self.modes.items():
            if window_class in mode_data['window_classes']:
                mode_names+=[mode_name]

        if len(mode_names)>0:
            self.set_current_mode(mode_names[0])
        else:
            self.set_current_mode('GenericMode')

    def lode_modules(self):

        self.run_in_background(Listener,
                               {'port':self.listener_port})
        self.run_in_background(Intender,
                               {'port':self.intender_port, 'modes_path':self.modes_path})

    def respond(self, r):
        
        try:

            if r['command']=='currentMode':
                msg={'status':'ok', 
                     'currentMode':self.current_mode,
                     'lastCommand': self.last_command,
                     'lastSpeech': self.last_speech,
                     }
            elif r['command']=='previousMode':
                msg={'status':'ok', 'previousMode':self.previous_mode}
            elif r['command']=='setCurrentMode':
                self.set_current_mode(r.get('mode_name'))
                msg={'status':'ok', 'currentMode':self.current_mode}
            elif r['command']=='setCurrentWindow':
                self.set_current_window()
                msg={'status':'ok', 'info':'updated mode based on window_class',}
            elif r['command']=='getAllModes':
                msg={'status':'ok', 'allModes':self.modes}
            elif r['command']=='setModeAction':
                mode_name=r['mode_name']
                mode_action=r['mode_action']
                intent_data=r.get('intent_data', {})
                slot_names=r.get('slot_names', {})
                self.act(mode_name, mode_action, slot_names, intent_data)
                msg={'status':'ok', 'action':'setModeAction', 'info': r}
            elif r['command']=='notify':
                self.act('NotifyMode', 'notifyAction', r, r)   
                msg={'status':'ok', 'action':'setListener'}
            elif r['command']=='updateListener':
                self.update_listener()
                msg={'status':'ok', 'action':'updateListener'}
            elif r['command']=='storeData':
                mode_store=self.mode_store_data.get(r['mode_name'])
                mode_store[r['data_name']]=r['data']
                msg={'status':'ok', 'action':'storeData'}
            elif r['command']=='accessStoreData':
                mode_store=self.mode_store_data.get(r['mode_name'], {})
                data=mode_store.get(r['data_name'], {})
                msg={'status':'ok', 'action':'accessStoreData', 'data':data}
            elif r['command']=='getModePorts':
                data=[]
                for r in self.modes.values():
                    data+=[{r['mode_name']:r['port']}]
                data+=[{'Handler':self.port}, {'Listener':self.listener_port}]
                msg={'status':'ok', 'action':'getModePorts', 'data':data}
            elif r['command']=='registerMode':
                self.modes[r['mode_name']]=r
                self.mode_store_data[r['mode_name']]={}
                self.create_socket(r)
                msg={'status':'ok', 'action': 'registeredMode', 'info': r['mode_name']}
            elif r['command']=='exit':
                msg={'status':'ok', 'info':'exiting'}
                self.exit()
            else:
                msg={'status':'nok', 'info':'request not understood'}

        except:

           err_type, error, traceback = sys.exc_info()
           msg={'status':'nok',
                 'info': 'an error has occured',
                 'error': str(error),
                 'agent': self.__class__.__name__}

        self.socket.send_json(msg)

    def create_socket(self, r):
        socket=zmq.Context().socket(zmq.PUSH)
        socket.connect(f'tcp://localhost:{r["port"]}')
        self.sockets[r['mode_name']]=socket

    def act(self, mode_name, command_name, slot_names={}, intent_data={}):
        if mode_name in self.modes:
            self.last_command=command_name.split('_')[-1]
            socket=self.sockets[mode_name]
            socket.send_json({'command': command_name,
                              'slot_names':slot_names,
                              'intent_data':intent_data,
                              })

    def listen(self):

        def start():
            while self.running:
                self.respond(self.socket.recv_json())
            print('Handler listener: exiting')

        handler_thread=threading.Thread(target=start)
        handler_thread.setDaemon(True)
        handler_thread.start()
        
    def run(self):

        def parse(text, mode_name=None):
            msg={'command':'parse', 'text':text, 'mode_name':mode_name}
            self.intender_socket.send_json(msg)
            r=self.intender_socket.recv_json()
            if r['status']=='ok' and  r['mode_name'] is not None:
                return r['mode_name'], r['c_name'], r['s_names'], r['i_data']
            else: 
                return None, None, {}, {}

        self.running=True
        self.set_current_window()

        while self.running:

            d=self.listener_socket.recv_json()

            self.last_speech=d['text']

            if d['text']=='exit':
                break
            elif d['text']=='private':
                self.private_mode=True
                self.set_current_mode('Private')
            elif d['text']=='listen':
                self.private_mode=False
                self.set_current_mode(self.previous_mode)

            if self.private_mode: continue

            c_name=None

            if self.current_mode != None:
                m_name, c_name, s_names, i_data = parse(d['text'], self.current_mode)

            if c_name is None:
                m_name, c_name, s_names, i_data = parse(d['text'])

            if c_name is None:
                text=self.interpreter.predict(d['text'])
                if text:
                    m_name, c_name, s_names, i_data = parse(text)

            print('Understood: ', m_name, c_name) 

            if self.current_mode != None:
                m_name=self.current_mode

            if c_name:
                self.set_current_mode(m_name)
                self.act(m_name, c_name, s_names, i_data)

        self.exit()
        print('Handler run: exiting')

    def exit(self, close_modes=True):
        self.running=False

        self.intender_socket.send_json({'command':'exit'})
        respond=self.intender_socket.recv_json()

        if close_modes:
            for mode_name in self.modes:
                self.act(mode_name, 'exit')

    def run_in_background(self, mode_class, kwargs):
        def start(mode_class, kwargs):
            app=mode_class(**kwargs)
            app.run()
        t=Process(target=start, args=(mode_class, kwargs))
        t.start()

if __name__=='__main__':
    app=Handler()
    app.run()

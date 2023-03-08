import zmq
import json
import threading

from multiprocessing import Process

from speechToCommand import modes

class Handler:
    def __init__(self, parent):
        self.parent=parent
        self.port=parent.handler_port
        self.socket=self.parent.handler_socket

        self.modes={}
        self.currentMode=None
        self.previousMode=None

        self.load_modes()

        self.running=True
        self.run()

    def set_current_mode(self, mode_name):
        self.previousMode=self.currentMode
        self.currentMode=mode_name

    def load_modes(self):

        def run(mode_class, parent_port):
            def start(mode_class, parent_port):
                app=mode_class(parent_port=parent_port)
                app.run()
            t=Process(target=start, args=(mode_class, parent_port))
            t.start()

        for m in modes.__dir__():
            if m.startswith('__'): continue
            mode_package=getattr(modes, m)
            mode_class=mode_package.get_mode()
            try:
                run(mode_class, self.port)
            except:
                print(f'Could not load: {mode_class.__name__}')

    def respond(self, r):
        
        try:

            if r['command']=='currentMode':
                msg={'status':'ok', 'currentMode':self.currentMode}
            elif r['command']=='previousMode':
                msg={'status':'ok', 'previousMode':self.previousMode}
            elif r['command']=='setCurrentMode':
                self.set_current_mode(r.get('mode_name'))
                msg={'status':'ok', 'currentMode':self.currentMode}
            elif r['command']=='setModeAction':
                mode_name=r['mode_name']
                mode_action=r['mode_action']
                intent_data=r['intent_data']
                self.parent.act(mode_name, mode_action, intent_data)
                msg={'status':'ok', 'action':'setModeAction'}
            elif r['command']=='registerMode':
                self.modes[r['mode_name']]=r
                self.create_socket(r)
                self.parent.intender.add_mode(r)
                self.parent.intender.update_parser()
                msg={'status':'ok', 'action': 'registeredMode'}
            else:
                msg={'status':'nok', 'info':'request not understood'}

            self.socket.send_json(msg)

        except:

            msg={'status':'nok',
                 'info': 'an error has occured',
                 'agent': self.__class__.__name__}
            self.socket.send_json(msg)

    def create_socket(self, r):
        socket=zmq.Context().socket(zmq.REQ)
        socket.connect(f'tcp://localhost:{r["port"]}')
        self.modes[r['mode_name']]['socket']=socket

    def act(self, mode_name, command_name, slot_names, intent_data):
        if mode_name in self.modes:
            socket=self.modes[mode_name]['socket']
            socket.send_json({'command': command_name,
                              'slot_names':slot_names,
                              'intent_data':intent_data})
            print(socket.recv_json())

    def run(self):

        def listen():
            while self.running:
                self.respond(self.socket.recv_json())

        reporterThread=threading.Thread(target=listen)
        reporterThread.setDaemon(True)
        reporterThread.start()

    def handle(self):

        def parse(*args, **kwargs):
            return self.parent.intender.parse(*args, **kwargs)

        def listen():
            return self.parent.listener_socket.recv_json()

        self.running=True

        while self.running:

            d=listen()

            if d['text']=='exit': self.parent.exit()

            m_name=None
            if self.currentMode != None:
                m_name, c_name, s_names, i_data = parse(d['text'], self.currentMode)
                if m_name is None:
                    m_name, c_name, s_names, i_data = parse(d['text'], 'ChangeMode')
                if m_name is None:
                    m_name, c_name, s_names, i_data = parse(d['text'], 'GenericMode')
                    if m_name == 'GenericMode': m_name=self.currentMode
            if self.currentMode is None or m_name is None:
                m_name, c_name, s_names, i_data = parse(d['text'])

            if m_name:
                self.set_current_mode(m_name)
                self.act(m_name, c_name, s_names, i_data)

    def exit(self, close_modes=True):
        self.running=False
        if close_modes:
            for m in self.modes:
                socket=self.modes[m]['socket']
                socket.send_json({'command':'exit'})
                print(socket.recv_json())

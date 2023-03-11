import sys
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
        self.mode_store_data={}
        self.sockets={}

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
                    
    def set_listener(self):
        self.parent.set_listener()
        for r in self.modes.values():
            self.parent.intender_socket_1.send_json(r)
            self.parent.intender_socket_2.send_json(r)
            self.parent.intender_socket_3.send_json(r)
            respond1=self.parent.intender_socket_1.recv_json()
            respond2=self.parent.intender_socket_2.recv_json()
            respond3=self.parent.intender_socket_3.recv_json()
            print('Respond from Intender: ', respond1)
            print('Respond from Intender: ', respond2)
            print('Respond from Intender: ', respond3)

    def respond(self, r):
        
        try:

            if r['command']=='currentMode':
                msg={'status':'ok', 'currentMode':self.currentMode}
            elif r['command']=='previousMode':
                msg={'status':'ok', 'previousMode':self.previousMode}
            elif r['command']=='setCurrentMode':
                self.set_current_mode(r.get('mode_name'))
                msg={'status':'ok', 'currentMode':self.currentMode}
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
            elif r['command']=='setListener':
                self.set_listener()
                msg={'status':'ok', 'action':'setListener'}
            elif r['command']=='storeData':
                mode_store=self.mode_store_data.get(r['mode_name'])
                mode_store[r['data_name']]=r['data']
                msg={'status':'ok', 'action':'storeData'}
            elif r['command']=='accessStoreData':
                mode_store=self.mode_store_data.get(r['mode_name'], {})
                data=mode_store.get(r['data_name'], {})
                msg={'status':'ok', 'action':'accessStoreData', 'data':data}
            elif r['command']=='registerMode':

                self.modes[r['mode_name']]=r
                self.mode_store_data[r['mode_name']]={}
                self.create_socket(r)


                self.parent.intender_socket_1.send_json(r)
                self.parent.intender_socket_2.send_json(r)
                self.parent.intender_socket_3.send_json(r)
                respond1=self.parent.intender_socket_1.recv_json()
                respond2=self.parent.intender_socket_2.recv_json()
                respond3=self.parent.intender_socket_3.recv_json()
                print('Respond from Intender: ', respond1)
                print('Respond from Intender: ', respond2)
                print('Respond from Intender: ', respond3)


                msg={'status':'ok', 'action': 'registeredMode'}


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
        if not self.currentMode in [None, 'GenericMode']:
            mode_name=self.currentMode
        print(mode_name, command_name, slot_names, self.modes.keys())
        if mode_name in self.modes:
            socket=self.sockets[mode_name]
            socket.send_json({'command': command_name,
                              'slot_names':slot_names,
                              'intent_data':intent_data})

    def run(self):

        def listen():
            while self.running:
                self.respond(self.socket.recv_json())

        reporterThread=threading.Thread(target=listen)
        reporterThread.setDaemon(True)
        reporterThread.start()

    def handle(self):

        def parse(text, mode_name):
            msg={'command':'parse', 'text':text, 'mode_name':mode_name}
            if not mode_name or type(mode_name)==str:
                mode_name=[mode_name]

            for i, m_name in enumerate(mode_name):
                intender=getattr(self.parent, f'intender_socket_{i+1}')
                msg['mode_name']=m_name
                intender.send_json(msg)
            rs=[]
            for i, m_name in enumerate(mode_name):
                intender=getattr(self.parent, f'intender_socket_{i+1}')
                rs+=[intender.recv_json()]

            chosen=None
            for i, r in enumerate(rs):
                # if i==0: chosen=r
                # if chosen['i_prob']<r['i_prob']: chosen=r
                if r['mode_name']!=None:
                    chosen=r
                    break

            if not chosen: return None, None, {}, {}
            r=chosen

            if r['status']=='ok':
                return r['mode_name'], r['c_name'], r['s_names'], r['i_data']

        def listen():
            return self.parent.listener_socket.recv_json()

        self.running=True

        while self.running:

            d=listen()

            if d['text']=='exit': self.parent.exit()

            m_name=None
            mode_names=[]
            if self.currentMode != None:
                for f in [self.currentMode, 'GenericMode', 'ChangeMode']:
                    if not f in mode_names: mode_names+=[f]
                m_name, c_name, s_names, i_data = parse(d['text'], mode_names) 
                if m_name == 'GenericMode': m_name=self.currentMode
            if self.currentMode is None or m_name is None:
                m_name, c_name, s_names, i_data = parse(d['text'], None)

            print('Understood: ', m_name, c_name) 
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

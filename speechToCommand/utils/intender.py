import re
import os
import sys
import zmq
import yaml
import inspect

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

class Intender(SnipsNLUEngine):

    def __init__(self, port=None, modes_path=None):
        super(Intender, self).__init__()

        self.port=port
        self.modes_path=modes_path
        self.intent_files=[]

        self.set_connection()
        self.set_intents()
        self.fit_parser()

    def set_connection(self):
        if self.port:
            self.socket = zmq.Context().socket(zmq.REP)
            self.socket.bind(f'tcp://*:{self.port}')

    def set_intents(self):
        if self.modes_path and os.path.exists(self.modes_path):
            for root, dirs, files in os.walk(self.modes_path):
                path = root.split(os.sep)
                for file in files:
                    if not file.endswith('yaml'): continue
                    self.intent_files+=[f'{root}/{file}']

    def fit_parser(self):
        self.dataset = Dataset.from_yaml_files(language='en', filenames=self.intent_files)
        self.fit(self.dataset.json)
        self.modes={}
        for intent in self.dataset.intents:
            mode_name=intent.intent_name.split('_')[0]
            if not mode_name in self.modes:
                self.modes[mode_name]=[]
            self.modes[mode_name]+=[intent.intent_name]

    def parse(self, text, m_name=None, prob=.5):

        def get_slot_names(intent_data):
            slot_name_to_value={}
            for s in intent_data['slots']:
                slot_name_to_value[s['slotName']]=s['value']['value']
            return slot_name_to_value

        intents=self.modes.get(m_name, None)
        i_data=super().parse(text, intents=intents)
        c_name=i_data['intent'].get('intentName', None)
        if c_name:
            m_name = c_name.split('_')[0]
            i_prob=i_data['intent']['probability']
            if prob<i_prob:
                s_names=get_slot_names(i_data)
                return m_name, c_name, s_names, i_data, i_prob
        return None, None, {}, i_data, 0


    def respond(self, r):

        try:

            if r['command']=='parse':
                r=self.parse(r['text'], r.get('mode_name', None))
                msg={'status':'ok',
                     'mode_name': r[0],
                     'c_name': r[1],
                     's_names': r[2],
                     'i_data': r[3],
                     'i_prob': r[4],
                     }
            elif r['command']=='saveSpeechData':
                msg={'status':'ok', 'info':'saving speech data'}
                self.save_utterences()
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

    def run(self):

        self.running=True
        while self.running:
            request=self.socket.recv_json()
            self.respond(request)

    def exit(self):
        self.running=False
        print('Internder: exiting')


import re
import os
import sys
import zmq
import yaml
import inspect

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

from snips_nlu_utils import hash_str
from snips_nlu.intent_parser.intent_parser import IntentParser
from snips_nlu.constants import (RES_INTENT, RES_INTENT_NAME)

class Intender(SnipsNLUEngine):

    def __init__(self, port, modes_path=None):
        super(Intender, self).__init__()

        self.port=port
        self.modes_path=modes_path
        self.intent_files=[]

        self.utterences={}

        self.set_connection()
        self.set_intents()
        self.update_parser()

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind(f'tcp://*:{self.port}')

    def set_intents(self):
        if self.modes_path and os.path.exists(self.modes_path):
            for root, dirs, files in os.walk(self.modes_path):
                path = root.split(os.sep)
                for file in files:
                    if 'intents.yaml' in file:
                        self.intent_files+=[f'{root}/{file}']

    def add_mode(self, data):
        pass
        # if type(data)==dict: data=[data,]
        # for r in data: 

            # if not r['intents_path']: continue

            # dataset = Dataset.from_yaml_files(language='en', filenames=[r['intents_path']])
            # intent_names=[i.intent_name for i in dataset.intents]

            # if not r['intents_path'] in self.intent_files:
            #     self.intent_files+=[r['intents_path']]
                # self.update_parser()

            # self.modes[r['mode_name']]={'dataset':dataset,
            #                             'path': r['intents_path'],
            #                             'intent_names': intent_names,
            #                             }

    def update_parser(self):
        # yaml_paths=[y['path'] for y in self.modes.values()]
        # dataset = Dataset.from_yaml_files(language='en', filenames=yaml_paths)
        self.dataset = Dataset.from_yaml_files(language='en', filenames=self.intent_files)
        # dataset = Dataset.from_yaml_files(language='en', filenames=self.intent_files)
        self.fit(self.dataset.json)

    def parse(self, text, m_name=None, prob=.5):


        def get_slot_names(intent_data):
            slot_name_to_value={}
            for s in intent_data['slots']:
                slot_name_to_value[s['slotName']]=s['value']['value']
            return slot_name_to_value

        if m_name:
            mode=self.modes.get(m_name, None)
            if mode:
                intent_names=mode.get('intent_names', None)
                i_data=super().parse(text, intents=intent_names)
            else:
                return None, None, {}, {}, 0
        else:
            i_data=super().parse(text)

        c_name=i_data['intent'].get('intentName', None)

        if c_name:

            m_name = c_name.split('_')[0]

            i_prob=i_data['intent']['probability']
            if prob<i_prob:
                s_names=get_slot_names(i_data)
                self.register_text(text, m_name, c_name, s_names, i_data)
                return m_name, c_name, s_names, i_data, i_prob

            else:
                return None, None, {}, i_data, 0

        else:
            return None, None, {}, i_data, 0

    def save_utterences(self, yaml_path='utterences/data.yaml'):
        with open(yaml_path, 'w') as file:
            yaml.dump(self.utterences, file)

    def register_text(self, text, m_name=None, c_name=None, s_names={}, i_data={}):

        results=self.find_candidates(self.intent_parsers[0], text)
        if results:
            txts=self.recreate_text(self.intent_parsers[0], results)
            for txt in txts:
                self.utterences[txt]=text
        # else:
            # todo: getting text from the probabilistic interpreter
            # self.speech.add(' '.join([s['value']['value'] for s in i_data['slots']]))

    def find_candidates(self, parser, text, top_n=1, intents=None):
        results =[] 
        for text_candidate, entities in parser._get_candidates(text, intents):
            val = parser._map.get(hash_str(text_candidate))
            if val is not None:
                result = parser._parse_map_output(text, val, entities, intents)
                if result:
                    intent_name = result[RES_INTENT][RES_INTENT_NAME]
                    results+=[(text_candidate, entities)]
        return results[:top_n]

    def recreate_text(self, parser, results):
        pttr=re.compile('% ([^ %]+) %')
        txts=[]
        for can, entities in results:
            for e in entities:
                can=pttr.sub(e['value'], can, 1) 
            txts+=[can]
        return txts


    def respond(self, r):

        # print(f'{self.__class__.__name__} request:', r)
        try:

            if r['command']=='registerModes':
                self.add_mode(r['modes_data'])
                msg={'status':'ok', 'info':'mode added'}
            elif r['command']=='parse':
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
        print('Internder: exiting')

    def exit(self):
        self.running=False
        # self.save_utterences()


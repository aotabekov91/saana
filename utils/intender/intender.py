import sys
import zmq
from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

import configparser

class Intender(SnipsNLUEngine):

    def __init__(self, port):
        super(Intender, self).__init__()

        self.modes={}
        self.port=port

        self.set_connection()

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind(f'tcp://*:{self.port}')

    def add_mode(self, r):
        if r['intents_path']:
            dataset = Dataset.from_yaml_files(language='en', filenames=[r['intents_path']])
            intent_names=[i.intent_name for i in dataset.intents]

            self.modes[r['mode_name']]={'dataset':dataset,
                                        'path': r['intents_path'],
                                        'intent_names': intent_names,
                                        }

    def update_parser(self):
        yaml_paths=[y['path'] for y in self.modes.values()]
        dataset = Dataset.from_yaml_files(language='en', filenames=yaml_paths)
        self.fit(dataset.json)

    def parse(self, text, m_name=None, prob=.3):
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
                s_names=self.get_slot_names(i_data)
                return m_name, c_name, s_names, i_data, i_prob
            else:
                return None, None, {}, i_data, 0

        else:
            return None, None, {}, i_data, 0
            
    def get_slot_names(self, intent_data):
        slot_name_to_value={}
        for s in intent_data['slots']:
            slot_name_to_value[s['slotName']]=s['value']['value']
        return slot_name_to_value

    def respond(self, r):

        try:

            if r['command']=='registerMode':
                self.add_mode(r)
                self.update_parser()

                msg={'status':'ok', 'info':'mode added'}
            elif r['command']=='parse':
                r=self.parse(r['text'], r['mode_name'])
                msg={'status':'ok',
                     'mode_name': r[0],
                     'c_name': r[1],
                     's_names': r[2],
                     'i_data': r[3],
                     'i_prob': r[4],
                     }
            elif r['command']=='exit':
                self.exit()
                msg={'status':'nok', 'info':'exiting'}
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
            print(request)
            self.respond(request)

    def exit(self):
        self.running=False

def test_intender_instance():
    config_path='/home/adam/bin/python/speechToCommand/config.ini'
    config=configparser.ConfigParser()
    config.read(config_path)
    intender=Intender(loader.load_modes())
    return intender

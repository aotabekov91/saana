import zmq
from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

import configparser

class Intender(SnipsNLUEngine):

    def __init__(self, parent=None):
        super(Intender, self).__init__()

        self.modes={}
        self.parent=parent

        self.set_connection()

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.REP)
        if self.parent.intender_port:
            self.socket.bind(f'tcp://*:{self.parent.intender_port}')
        else:
            self.parent.intender_port=self.socket.bind_to_random_port(f'tcp://*')

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
                return None, None, {}, {}
        else:
            i_data=super().parse(text)

        c_name=i_data['intent'].get('intentName', None)

        if c_name:

            m_name = c_name.split('_')[0]

            if prob<i_data['intent']['probability']:
                s_names=self.get_slot_names(i_data)
                return m_name, c_name, s_names, i_data
            else:
                return None, None, {}, i_data

        else:
            return None, None, {}, i_data
            
    def get_slot_names(self, intent_data):
        slot_name_to_value={}
        for s in intent_data['slots']:
            slot_name_to_value[s['slotName']]=s['value']['value']
        return slot_name_to_value

    def run(self):
        pass

    def exit(self):
        pass

def test_intender_instance():
    config_path='/home/adam/bin/python/speechToCommand/config.ini'
    config=configparser.ConfigParser()
    config.read(config_path)
    loader=Loader(config)
    intender=Intender(loader.load_modes())
    return intender

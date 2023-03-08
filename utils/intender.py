import zmq
from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset

import configparser
from speechToCommand.utils.loader import Loader


class Intender(SnipsNLUEngine):

    def __init__(self, modes=None):
        super(Intender, self).__init__()
        self.modes=modes
        self.get_dataset()
        self.fit(self.json)

    def get_dataset(self):
        self.dataset={}
        paths=[]
        for mode_name, (mode_class, port) in self.modes.items():
            ypath=mode_class.intents_yaml_paths
            paths+=ypath
            dataset = Dataset.from_yaml_files(language='en', filenames=ypath)
            self.dataset[mode_name]=dataset
        # <todo loader should do it automatically  
        path='/home/adam/bin/python/speechToCommand/intents.yaml'
        dataset = Dataset.from_yaml_files(language='en', filenames=[path])
        self.dataset['GenericMode']=dataset
        paths+=[path]
        #>todo
        dataset = Dataset.from_yaml_files(language='en', filenames=paths)
        self.json=dataset.json

    def parse(self, text, mode_name=None, probability_threshold=.3):
        if mode_name:
            mode_dataset=self.dataset.get(mode_name, None)
            if mode_dataset:
                mode_intents=[i.intent_name for i in mode_dataset.intents]
                intent_data=super().parse(text, intents=mode_intents)
            else:
                return None, None, None
        else:
            intent_data=super().parse(text)

        if len(intent_data)>0:
            intent_name=intent_data['intent'].get('intentName', None)
            if intent_name is None: return None, None, intent_data
            mode_name, action_name=tuple(intent_name.split('_'))
            if intent_data['intent']['probability']>=probability_threshold:
                return mode_name, intent_name, intent_data
            else:
                return None, None, intent_data
        else:
            return None, None, intent_data

def test_intender_instance():
    config_path='/home/adam/bin/python/speechToCommand/config.ini'
    config=configparser.ConfigParser()
    config.read(config_path)
    loader=Loader(config)
    intender=Intender(loader.load_modes())
    return intender

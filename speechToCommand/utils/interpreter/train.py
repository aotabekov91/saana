import re
import os
import zmq
import json
import yaml

import threading

from speechToCommand.utils.intender import Intender
from speechToCommand.utils.listener import Listener

class Trainer:

    def __init__(self, 
                 yaml_path='/home/adam/bin/python/speechToCommand/utils/interpreter/model/data.sav',
                 mode_path='/home/adam/bin/python/speechToCommand/modes', 
                 intender_port=9723,
                 listener_port=19833,
                 ):

        self.yaml_path=yaml_path

        self.intender=Intender(intender_port, mode_path)
        self.listener=Listener(listener_port)

        self.socket=zmq.Context().socket(zmq.PULL)
        self.socket.connect(f'tcp://localhost:{listener_port}')

        self.set_intender_data()


    def set_intender_data(self):

        def _get(dt, level=0, _list=['']):
            to_add=[]
            if not level+1 in dt:
                for f in dt[level]:
                    for i, j in enumerate(_list):
                        to_add+=[' '.join([j, f])]
            else:
                for f in dt[level]:
                    for i, j in enumerate(_list):
                        to_add+=[' '.join([j, f])]
                to_add=_get(dt, level+1, to_add)
            return to_add


        entities={}
        for e in self.intender.dataset.entities:
            entities[e.name]=[]
            for u in e.utterances:
                entities[e.name]+=[u.value]
                entities[e.name]+=u.synonyms


        y_data={}
        for intent in self.intender.dataset.intents:
            for utterance in intent.utterances:
                alts={}
                for i in range(len(utterance.chunks)):
                    alts[i]=[]
                for i, c in enumerate(utterance.chunks):
                    alts[i]+=[c.text]
                    if hasattr(c, 'entity') and c.entity in entities:
                        for e in entities[c.entity]:
                            alts[i]+=[e]
                if len(alts)==1:
                    for a in alts[0]:
                        y_data[a]=[]
                else:
                    list_=_get(alts)
                    for f in list_:
                        f=re.sub('  *', ' ', f).strip()
                        y_data[f]=[]
        self.y_data=y_data

    def save_data(self):
        # todo: shoudl remove move yaml clean data those commands that depricated due to the changes in intent yamls
        clean_data=self.get_yaml_data()
        for f in self.y_data:
            if not f in clean_data:
                clean_data[f]=self.y_data[f]
            else:
                clean_data[f]+=self.y_data[f]
            clean_data[f]=list(set(clean_data[f]))
        yaml.safe_dump(clean_data, open(self.yaml_path, 'w'))
        

    def get_yaml_data(self):
        y_data=yaml.safe_load(open(self.yaml_path, 'r'))
        clean_up={}
        for i, j in y_data.items():
            j=set(j)
            clean_up[i]=list(j)
        return clean_up


    def run(self):

        def _run_listener():
            self.listener.run()

        t=threading.Thread(target=_run_listener)
        t.daemon=True
        t.start()

        os.system('clear')


        for phrase, data in self.y_data.items():

            self.y_data[phrase]+=[phrase]

            words=phrase.split(' ')

            for i in range(2):
                for word in words:
                    print(f'Say: {word}')
                    l=self.socket.recv_json()
                    text=l['text']
                    print(f'You said: {text}')
                    if word!=text:
                        if word in self.y_data:
                            if not word in self.y_data: self.y_data[word]+=[word]
                            self.y_data[word]+=[text]
                        else:
                            self.y_data[word]=[word, text]

        self.save_data()


if __name__=='__main__':
    app=Trainer()
    app.run()

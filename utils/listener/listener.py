import os
import zmq
import json
import time

import speech_recognition as sr
from vosk import Model, KaldiRecognizer

def callback(listener, audio):
    command=json.loads(listener.recognize_vosk(audio))
    if command['text']!='':
        if command['text']=='stop listening':
            listener.deactivate()
        else:
            try:
                # listener.send_json(command, zmq.NOBLOCK)
                listener.send_json(command)
            except:
                pass

class Listener(sr.Recognizer):

    def __init__(self, config=None):
        super().__init__()
        self.config=config
        self.set_connection()
        self.set_vosk()
        self.set_microphone()
        self.activate()

    def set_connection(self):
        if self.config!=None:
            self.port=int(self.config['port'])
            self.scontext = zmq.Context()
            self.ssocket = self.scontext.socket(zmq.PUSH)
            self.ssocket.bind(f'tcp://*:{self.port}')
        else:
            self.port=None

    def send_json(self, data):
        print('Listener: ', data['text'])
        if self.port: 
            self.ssocket.send_json(data)

    def set_vosk(self):
        mode_dir=os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(f'{mode_dir}/model'): return "Please download the model"
        self.vosk_model = Model(f'{mode_dir}/model')
        self.rec = KaldiRecognizer(self.vosk_model, 36000);
        
    def recognize_vosk(self, audio_data, language='en'):
        self.rec.AcceptWaveform(audio_data.get_raw_data(convert_rate=36000, convert_width=2));
        finalRecognition = self.rec.FinalResult()
        return finalRecognition
    
    def set_microphone(self):
        self.mic=sr.Microphone()
        with self.mic as source:
            self.adjust_for_ambient_noise(source)

    def activate(self):
        self.stopFunction=self.listen_in_background(self.mic, callback)

    def deactivate(self):
        self.stopFunction()

if __name__=='__main__':
    listener=Listener()
    listener.activate()
    while True:
        time.sleep(1)

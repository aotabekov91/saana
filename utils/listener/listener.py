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

    def __init__(self, parent=None): 
        super().__init__()
        self.parent=parent

        self.set_connection()

        self.set_vosk()
        self.set_microphone()
        self.run()

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.PUSH)
        if self.parent.listener_port:
            self.socket.bind(f'tcp://*:{self.parent.listener_port}')
        else:
            self.parent.listener_port=self.socket.bind_to_random_port(f'tcp://*')

    def send_json(self, data):
        print('Listener: ', data['text'])
        self.socket.send_json(data)

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

    def run(self):
        self.stopFunction=self.listen_in_background(self.mic, callback)

    def exit(self):
        self.stopFunction()

if __name__=='__main__':
    listener=Listener(port=33333)
    listener.run()
    while True:
        time.sleep(1)

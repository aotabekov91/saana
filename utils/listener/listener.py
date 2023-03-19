import os
import zmq
import json
import time

import threading

import speech_recognition as sr
from vosk import Model, KaldiRecognizer

class Listener(sr.Recognizer):

    def __init__(self, port=None): 
        super().__init__()
        self.port=port
        self.running=False

        self.set_connection()

        self.set_vosk()
        self.set_microphone()

    def set_connection(self):
        self.socket = zmq.Context().socket(zmq.PUSH)
        self.socket.bind(f'tcp://*:{self.port}')

    def send_json(self, data):
        print('Listener: ', data['text'])
        self.socket.send_json(data, zmq.NOBLOCK)

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
        def threaded_listen():
            with self.mic as s:
                while self.running:
                    try: 
                        audio = self.listen(s, 1, None)
                    except Exception:  # listening timed out, just try again
                        pass
                    else:
                        if self.running: self.callback(audio)

        self.running=True
        listener_thread = threading.Thread(target=threaded_listen)
        listener_thread.daemon = True
        listener_thread.start()

        listener_thread.join()

    def callback(self, audio):
        command=json.loads(self.recognize_vosk(audio))
        if command['text']=='':
            return
        elif command['text']=='stop listening':
            self.exit()
        else:
            try:
                self.send_json(command)
            except:
                pass

    def exit(self):
        self.running=False

if __name__=='__main__':

    listener=Listener(port=33333)
    listener.run()

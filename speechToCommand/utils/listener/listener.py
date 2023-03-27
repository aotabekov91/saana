import os
import zmq
import json
import pyaudio

import speech_recognition as sr
from vosk import Model, KaldiRecognizer

class Listener(sr.Recognizer):

    def __init__(self, port=None): 
        super().__init__()
        self.port=port
        self.running=False

        self.energy_threshold = 25  # minimum audio energy to consider for recording
        self.pause_threshold = 0.1  # seconds of non-speaking audio before a phrase is considered complete
        self.non_speaking_duration = 0.05  # seconds of non-speaking audio to keep on both sides of the recording

        self.set_connection()

        self.set_vosk()
        self.set_microphone()

    def set_connection(self):
        if self.port:
            self.socket = zmq.Context().socket(zmq.PUSH)
            self.socket.bind(f'tcp://*:{self.port}')

    def send_json(self, data):
        if self.port:
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

        # audio=pyaudio.PyAudio()
        # for i in range(audio.get_device_count()):
        #     info=audio.get_device_info_by_index(i)
        #     if 'Razer Seiren Elite Digital Stereo' in info['name']:
        #         index=info['index']
        #         break

        # index=None
        # for i in range(audio.get_device_count()):
        #     info=audio.get_device_info_by_index(i)
        #     if 'Razer Seiren Elite Digital Stereo' in info['name']:
        #         index=i

        # print(index)
        self.mic=sr.Microphone(chunk_size=128)

        with self.mic as source:
            self.adjust_for_ambient_noise(source)

    def run(self):

        self.running=True
        with self.mic as s:
            while self.running:
                try: 
                    audio = self.listen(s, 1, None)
                except Exception:  # listening timed out, just try again
                    pass
                else:
                    self.callback(audio)
        print('Listener: exiting')

    def callback(self, audio):
        command=json.loads(self.recognize_vosk(audio))
        if command['text']=='':
            return
        else:
            print('Listener: ', command['text'])
            self.send_json(command)
            if command['text']=='exit':
                self.exit()


    def exit(self):
        self.running=False

if __name__=='__main__':

    listener=Listener()
    listener.run()

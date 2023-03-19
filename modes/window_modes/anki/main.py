import os
import re
import sys
import zmq
import time
import hashlib
import playsound
import subprocess
import threading

import asyncio
from i3ipc.aio import Connection

from speechToCommand.utils.helper import osAppCommand
from speechToCommand.utils.moder import BaseGenericMode

class AnkiMode(BaseGenericMode):
    def __init__(self,
                 keyword='anki', 
                 info='AnkiMode', 
                 port=None, 
                 parent_port=None, 
                 config=None, 
                 window_classes=['anki', 'Anki'],
                 anki_port=None,
                 anki_media=None,
                 ):

        self.anki_port=anki_port
        self.anki_media=anki_media

        super(AnkiMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                )

    def set_config(self):
        super().set_config()
        self.anki_port=self.config.getint('Custom', 'anki_port')
        self.anki_media=self.config.get('Custom', 'anki_media_folder')

    def set_connection(self):
        super().set_connection()
        if self.anki_port:
            self.anki_socket=zmq.Context().socket(zmq.REQ)
            self.anki_socket.connect(f'tcp://localhost:{self.anki_port}')

    def get_reviewer_state(self):
        if self.anki_port:
            self.anki_socket.send_json({'command':'reviewerState'})
            respond=self.anki_socket.recv_json()
            reviewer_state=respond.get('reviewer_state', None)
            if reviewer_state=='question':
                plhld='_w'
            else:
                plhld=''
            return plhld

    def get_card_data(self):
        if self.anki_port:
            self.anki_socket.send_json({'command':'currentCardData'})
            respond=self.anki_socket.recv_json()
            return respond.get('data', None)

    def play_sound(self, path_raw):

        def get_sound_name(text):
            match=re.match('\[[^:]*:(.*)\]', text)
            if match and  match.group(1):
                return match.group(1)
        path=get_sound_name(path_raw)
        full_path=os.path.join(self.anki_media, path)
        t=threading.Thread(target=playsound.playsound, args=(full_path,))
        t.start()

    def generate(self, text, kind='sound'):

        def strip_text(text):
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'&nbsp;', ' ', text)
            text = re.sub(r'\\\\', '', text)
            text = re.sub("[^a-zA-Z0-9äßüöÄÜÖ \-\n\.,()'!?]", ' ', text)
            return re.sub('  *', ' ', text).strip()

        text=strip_text(text)

        if text=='': return None, None

        if kind=='sound':
            sound_name = f'{hashlib.md5(text.encode()).hexdigest()}.wav'
        elif kind=='image':
            sound_name = f'{hashlib.md5(text.encode()).hexdigest()}.jpg'

        sound_path=os.path.join(self.anki_media, sound_name)
        
        if os.path.isfile(sound_path) and kind=='sound':
            return sound_name, sound_path

        elif self.parent_port:
            self.parent_socket.send_json({
                'command': 'setModeAction',
                'mode_name': 'GeneratorMode',
                'mode_action': 'generateAction',
                'slot_names': {'kind': kind, 'save_path': sound_path, 'text':text}
                })
            respond=self.parent_socket.recv_json()
            print(respond)
            return sound_name, sound_path
        else:
            return None, None

    @osAppCommand()
    def refreshAction(self, request={}):
        self.anki_socket.send_json({'command':'refreshReviewer'})
        respond=self.anki_socket.recv_json()
        print(respond)

    @osAppCommand()
    def generateAction(self, request={}):

        slot_names=request['slot_names']
        kind=slot_names.get('kind', None)

        if not kind: return
        data=self.get_card_data()
        if not data: return
        nid=data['nid']

        new_data={}

        if kind=='sound':
            for field, value in data['field_values'].items():
                if '_s' in field: 
                    text=data['field_values'][field.replace('_s', '')]
                    name, path=self.generate(text, kind='sound')
                    if name: new_data[field]=f'[sound:{name}]'
        elif kind=='image':

            if 'Image' in data['field_values']:
                meaning=data['field_values'].get('Meaning', '')
                word=data['field_values'].get('Word', '')
                name, path=self.generate(f'{word} - {meaning}', kind='image')
                new_data={'Image':f'<img src="{name}">'}

        if len(new_data)>0:

            self.anki_socket.send_json(
                    {'command':'updateNote', 'data':new_data, 'nid':nid})
            respond=self.anki_socket.recv_json()
            print(respond)

    @osAppCommand()
    def examplePlayAction(self, request):
        plhld =self.get_reviewer_state()
        if plhld==None: return
        data=self.get_card_data()
        if not data: return
        slot_names=request['slot_names']
        number=int(slot_names.get('number', 1.))
        path_raw=data['field_values'][f'Example {"I"*number}{plhld}_s']
        if path_raw: self.play_sound(path_raw) 

    @osAppCommand()
    def frontPlayAction(self, request):
        plhld =self.get_reviewer_state()
        if plhld==None: return
        data=self.get_card_data()
        if not data: return
        if data['card_type']=='Learning':
            path_raw=data['field_values'][f'Meaning_s']
        else:
            path_raw=data['field_values'][f'Word_s']
        if path_raw: self.play_sound(path_raw) 

    @osAppCommand()
    def backPlayAction(self, request):
        plhld =self.get_reviewer_state()
        if plhld==None: return
        data=self.get_card_data()
        if not data: return
        if data['card_type']=='Learning':
            path_raw=data['field_values'][f'Word_s']
        else:
            path_raw=data['field_values'][f'Meaning_s']
        if path_raw: self.play_sound(path_raw) 

    @osAppCommand()
    def showAction(self, request={}):
        return 'xdotool getactivewindow key space'

    @osAppCommand()
    def moveLeftAction(self, request={}):
        plhld =self.get_reviewer_state()
        if plhld=='_w': self.showAction({})
        return 'xdotool getactivewindow type 1'

    @osAppCommand()
    def moveRightAction(self, request={}):
        plhld =self.get_reviewer_state()
        if plhld=='_w': self.showAction({})
        return 'xdotool getactivewindow type 3'

    @osAppCommand()
    def moveDownAction(self, request={}):
        plhld =self.get_reviewer_state()
        if plhld=='_w': self.showAction({})
        return 'xdotool getactivewindow type 2'

    @osAppCommand()
    def moveUpAction(self, request={}):
        plhld =self.get_reviewer_state()
        if plhld=='_w': self.showAction({})
        return 'xdotool getactivewindow type 4'

    @osAppCommand()
    def fullscreenAction(self, request={}):
        return 'xdotool getactivewindow type F'

if __name__=='__main__':
    app=AnkiMode(port=33333, parent_port=44444)
    app.run()

import os
import re
import sys
import langid
import html
import shutil
import threading
import queue
import requests
import html
import urllib.request
import urllib.parse
import fake_useragent

import openai


from speechToCommand.utils.moder import BaseGenericMode

openai.api_key=os.environ['OPEN_AI_API']

def translate(to_translate, to_language="auto", from_language="auto", wrap_len="80"):
    base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
    to_translate = urllib.parse.quote(to_translate)
    link = base_link % (to_language, from_language, to_translate)
    ua=fake_useragent.UserAgent()
    agent={'User-Agent': str(ua.random)}
    request = urllib.request.Request(link, headers=agent)
    raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="result-container">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) > 0): return re_result[0]

class GeneratorMode(BaseGenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(GeneratorMode, self).__init__(
                 keyword='generator', 
                 info='GeneratorMode', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.client=None
        self.content=None
        self.queue=queue.Queue()
        self.set_synthesizers()
        self.listen()

    def listen(self):

        def run():
            self.running=True
            while self.running:
                try:

                    kind, save_path, text =self.queue.get()
                    print('GeneratorMode received order: ', kind,  text, save_path)
                    if kind=='sound':
                        self.synthesize_sound(text, save_path)
                    elif kind=='image':
                        self.synthesize_image(text, save_path)
                    elif kind=='joke':
                        self.synthesize_joke()
                    elif kind=='quote':
                        self.synthesize_quote()
                except:
                    print('Error in the GeneratorMode')

        t=threading.Thread(target=run)
        t.daemon=True
        t.start()

    def set_synthesizers(self):

        try:

            from TTS.utils.manage import ModelManager
            from TTS.utils.synthesizer import Synthesizer

            # todo these three linse should be in config file
            en_model_name='tts_models/en/ljspeech/vits'
            de_model_name='tts_models/de/thorsten/vits'
            path = os.path.expanduser(
                    "/home/adam/.venv/speech/lib/python3.10/site-packages/TTS/.models.json")

            model_manager = ModelManager(path)

            model_path, config_path, model_item = model_manager.download_model(en_model_name)
            self.en_syn = Synthesizer(tts_checkpoint=model_path, tts_config_path=config_path)

            model_path, config_path, model_item = model_manager.download_model(de_model_name)
            self.de_syn = Synthesizer(tts_checkpoint=model_path, tts_config_path=config_path)

        except:

            self.de_syn=None
            self.en_syn=None

    def synthesize_image(self, text='beautiful city', path='city.jpg', size='512x512'):

        def save_image(url, path):
            def run(url, path):
                ua=fake_useragent.UserAgent()
                header={'User-Agent': str(ua.random)}
                r = requests.get(url, headers=header, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open(path,'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    print(f'File saved: {path}')
            p=threading.Thread(target=run, args=(url, path,))
            p.daemon=True
            p.start()

        def run(text, path, size):
            data=openai.Image.create(prompt=text, n=1, size=size)
            if len(data)>0:
                url=data['data'][0]['url']
                print('Image created')
                save_image(url, path)

        self.content=path

        lan=self.detect_lan(text)
        if lan=='de': text=translate(text, 'en')

        p=threading.Thread(target=run, args=(text, path, size))
        p.daemon=True
        p.start()

    def detect_lan(self, text):
        r = langid.classify(text)
        if r: return r[0]

    def synthesize_sound(self, text='I like this idea!', path='idea.wav'):

        def strip_text(data):
            return re.sub(r'<.*?>', ' ', data).strip()

        def run(text, path, lan):
            if lan=='en':
                syn=self.en_syn
            elif lan=='de':
                syn=self.de_syn
            outputs = syn.tts(f'{text}')
            syn.save_wav(outputs, path)
            print('Sound generated')

        clean_text=strip_text(text)
        lan=self.detect_lan(clean_text)
        if not lan in ['de', 'en']: return
        if not self.en_syn: return

        self.content=path

        p=threading.Thread(target=run, args=(text, path, lan))
        p.deamon=True
        p.start()

    def synthesize_quote(self):
        pass

    def synthesize_joke(self):
        pass
    
    def generateAction(self, request={}):
        slot_names=request.get('slot_names', None)
        if slot_names:

            self.client=slot_names.get('client', None)
            self.client_action=slot_names.get('action', None)

            kind=slot_names['kind']
            save_path=slot_names.get('save_path', None)
            text=slot_names.get('text', None)

            self.queue.put((kind, save_path, text))


    def confirmAction(self, request={}):

        if self.parent_port and self.client:
            self.parent_socket.send_json({
                'command': 'setModeAction',
                'mode_name': self.client,
                'mode_action': self.client_action,
                'slot_names': {'text':self.content},
                })
            respond=self.parent_socket.recv_json()
            print(respond)
        self.client=None
        self.content=None

if __name__=='__main__':
    app=GeneratorMode(port=33333)
    app.synthesize_image()
    app.synthesize_sound()
    app.run()

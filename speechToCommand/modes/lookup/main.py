import sys
import zmq

from multiprocessing import Process

from .anki_notes import *
from generator import finish_processes

from speechToCommand.utils.moder import GenericMode
from speechToCommand.utils.widgets import ListWindow

class LookupMode(GenericMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(LookupMode, self).__init__(
                 keyword='lookup', 
                 info='Lookup', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.lan='en'
        self.word=None

        self.ui=ListWindow(self, 'Lookup - own_floating', 'Word: ')

    def lookupAction(self, request):
        slot_names=request['slot_names']
        lan=slot_names.get('lan', None)
        if lan:
            self.lan=lan
            self.activateInput('getTextAction')

    def getTextAction(self, request):
        text=super().getTextAction(request)
        self.ui.setText(text)
        self.ui.show()
        self.confirmAction(request)

    def submitToAnki(self, request):
        pass
        # todo
        # asyncio.run(anki_submit(anki_notes))

    def refreshAction(self, request):
        # todo, e.g., after images have been downloaded
        pass

    def confirmAction(self, request={}):
        processes=[]
        text=self.ui.text()
        self.notes=get_anki_notes(text, self.lan, processes)
        self.set_label(self.notes)
        self.set_data(self.notes)
        finish_processes(processes, block=False)

    def doneAction(self, request={}):
        self.ui.label.setText('')
        self.ui.doneAction()

    def set_label(self, notes):

        word=notes[0]['fields']['Word']
        sound=notes[0]['fields']['Word']
        ipa=notes[0]['fields']['IPA']
        gender=notes[0]['fields'].get('Gender', '')
        plural=notes[0]['fields'].get('Plural', '')
        

        label="{}{}{}{}{}{}{}".format(gender,
                                      " "*bool(gender),
                                      f'{word} ',
                                      plural,
                                      " "*bool(plural),
                                      ipa,
                                      " "*bool(plural), 
                                      )
        self.ui.setText(word)
        self.ui.setLabel(label)

    def set_data(self, notes):
        self.dlist=[]
        for n in notes:
            self.dlist+=[{'top':n['fields']['Meaning'],
               'down': n['fields'].get('Example I'),
               'icon': n.get('picture_loc'),
                'sound_pronunciation': self.get_sound_path(n),
                'sound_down': self.get_sound_path(n, 'example'),
                'sound_top': self.get_sound_path(n, 'meaning'),
                'note': n,
               }]
        self.ui.addWidgetsToList(self.dlist)

    def get_sound_path(self, n, kind='pronunciation'):
        sounds_list=n.get('audio')
        if len(sounds_list)>0:
            if kind=='pronunciation':
                for f in sounds_list:
                    if 'Sound' in f['fields']: return f['path']
            elif kind=='example':
                for f in sounds_list:
                    if 'Example I sound' in f['fields']: return f['path']
            elif kind=='meaning':
                for f in sounds_list:
                    if 'Meaning_s' in f['fields']: return f['path']

if __name__ == '__main__':
    app = LookupMode(port=33333)
    app.run()

import sys
import zmq

from playsound import playsound
from multiprocessing import Process

from .utils import *
from generator import finish_processes

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class LookupMode(QBaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(LookupMode, self).__init__(
                 keyword='lookup', 
                 info='Lookup', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.lan='en'
        self.word=None
        self.notes=None

        self.ui=ListMainWindow(self, 'Lookup - own_floating', 'Word: ')

    def lookupAction(self, request):
        slot_names=request['slot_names']
        self.word=slot_names.get('word', '')
        self.lan=slot_names.get('lan', 'en')

        self.ui.edit.setText(self.word)
        self.ui.show()

    def playPronunciationAction(self, request):
        if self.notes:
            sounds_list=self.notes[0].get('audio')
            if len(sounds_list)>0:
                sound_path=sounds_list[0]['path']
                playsound(sound_path, block=False)

    def playSoundAction(self, request):
        if self.ui.isVisible():
            item=self.ui.list.currentItem()
            if not item: return
            sounds_list=item.itemData.get('sound', [])
            if len(sounds_list)>1:
                sound_path=sounds_list[1]['path']
                playsound(sound_path, block=False)

    def submitToAnki(self, request):
            pass
            # todo
            # asyncio.run(anki_submit(anki_notes))

    def refreshAction(self, request):
            # todo, e.g., after images have been downloaded
            pass

    def confirmAction(self, request={}):
        processes=[]
        text=self.ui.edit.text()
        self.notes=get_anki_notes(text, self.lan, processes)
        self.set_label(self.notes)
        self.set_data(self.notes)
        finish_processes(processes, block=False)

    def doneAction(self, request={}):
        self.ui.label.setText('')
        super().ui.doneAction()

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
        self.ui.edit.setText(word)
        self.ui.label.setText(label)
        self.ui.label.show()

    def set_data(self, notes):
        self.dlist=[]
        for n in notes:
            self.dlist+=[{'top':n['fields']['Meaning'],
               'down': n['fields'].get('Example I'),
               'icon': n.get('picture_loc'),
               'sound': n.get('audio'),
                'note': n,
               }]
        self.ui.addWidgetsToList(self.dlist)

if __name__ == '__main__':
    app = LookupMode(port=33333)
    app.run()

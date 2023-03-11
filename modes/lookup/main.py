import sys
import zmq

from playsound import playsound
from multiprocessing import Process

from generator import finish_processes

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

from .notes import get_anki_notes

class LookupMode(QBaseMode):
    def __init__(self, config):

        super(LookupMode, self).__init__(config, keyword='look up', info='Lookup')
        self.notes=None
        self.ui=ListMainWindow('Lookup - own_floating', 'Word: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.ui.confirm_signal.connect(self.confirmAction)
        self.ui.done_signal.connect(self.doneAction)


        def lookupEnglish(self, request):
            _, __, ___, slots=self.parse_request(request)
            if not slots: return
            request=slots[0]['value']['value']
            self.lan='en'
            self.ui.edit.setText(request)
            self.ui.show()

        elif request['command']=='LookupMode_lookupGerman':
            _, __, ___, slots=self.parse_request(request)
            if not slots: return
            request=slots[0]['value']['value']
            self.lan='de'
            self.ui.edit.setText(request)
            self.ui.show()
        elif request['command']=='LookupMode_playSound':
            if self.notes:
                sounds_list=self.notes[0].get('audio')
                if len(sounds_list)>0:
                    sound_path=sounds_list[0]['path']
                    playsound(sound_path, block=False)
        elif request['command']=='LookupMode_submitToAnki':
            pass
            # todo
            # asyncio.run(anki_submit(anki_notes))
        elif request['command']=='LookupMode_refreshAction':
            # todo
            if hasattr(self, 'dList'):
                self.ui.addWidgetsToList(self.dlist)
                self.ui.show()
        else:
            super().handleRequest(request)

    def confirmAction(self, request={}):
        processes=[]
        text=self.ui.edit.text()
        self.notes=get_anki_notes(text, self.lan, processes)
        self.set_label(self.notes)
        self.set_data(self.notes)
        finish_processes(processes, block=False)

    def doneAction(self, request={}):
        self.ui.label.setText('')

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
    app = LookupMode({})
    app.ui.show()
    sys.exit(app.exec_())

# importing libraries
import sys
import argparse
import asyncio
import playsound
import threading

from get_definition import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from pyqt_widgets.qlist import MainWindow

class LookupMainWindow (MainWindow):
    def __init__ (self):
        super(LookupMainWindow, self).__init__('tcp://*:5590')
        self.setWindowTitle('WordLookUp - own_floating')
        self.label.setText('Word')

    def handleRequest(self, request):
        if request['command']=='sound':
            self.show()
            play_sound(self.anki_notes)
            #todo
        elif request['command']=='lookup':
            _, self.anki_notes=get_notes(request['word'], request['lan'])
            self.setData(self.anki_notes)
            self.show()
        elif request['command']=='save':
            pass
            #todo
            # asyncio.run(anki_submit(anki_notes))
        else:
            super().handleRequest(request)

    def inputReturnPressed(self):
        text=self.edit.text()
        _, self.anki_notes=get_notes(text, 'en')
        self.setData(self.anki_notes)

    def inputTextChanged(self, text):
        pass

    def setInfo(self, notes):
        word=notes[0]['fields']['Word']
        sound=notes[0]['fields']['Word']
        self.edit.setText(word)
        ipa=notes[0]['fields']['IPA']
        gender=notes[0]['fields'].get('Gender', '')
        plural=notes[0]['fields'].get('Plural', '')
        label="{}{}{}{}{}{}{}".format(gender,
                                      " "*bool(gender),
                                      word,
                                      " "*bool(plural),
                                      plural,
                                      " "*bool(plural), 
                                      ipa)
        self.label.setText(label)
        self.label.show()

    def setData(self, notes):
        self.setInfo(notes)
        dlist=[]
        for n in notes:
            dlist+=[{'top':n['fields']['Meaning'],
               'down': n['fields'].get('Example I'),
               'icon': n.get('picture_loc'),
               'sound': n.get('audio'),
               }]
        self.addWidgetsToList(dlist)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.close()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication([])
    window = LookupMainWindow()
    sys.exit(app.exec_())

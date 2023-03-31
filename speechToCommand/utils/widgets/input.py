from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import command
from .components import MainWindow, InputWidget

class InputWindow (MainWindow):

    def __init__(self, mode, window_title='', label_title=''):
        super(InputWindow, self).__init__(mode, window_title)

        self.style_sheet='''
            QWidget#containerInput{
                font-size: 20px;
                border-width: 0px;
                border-radius: 0px;
                border-style: outset;
                border-width: 0px;
                color: white;
                border-radius: 10px;
                background-color: green;
                }
                '''

        self.setGeometry(0, 0, 700, 100)
        self.input=InputWidget(self)
        self.input.setLabel(label_title)
        self.setStyleSheet(self.style_sheet)

        self.setCentralWidget(self.input)

        self.input.returnPressed.connect(self.mode.confirmAction)

    def clear(self):
        self.input.clear()

    def label(self):
        return self.input.label()

    def setLabel(self, text):
        self.input.setLabel(text)

    def text(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText(text)

    @command(checkActionOnFinish=True, checkWindowType=False)
    def doneAction(self, request={}):
        self.input.clear()
        self.hide()

    def showAction(self, request={}):
        self.hide()
        self.show()
        self.input.setFocus()

    def setFocus(self):
        self.input.setFocus()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.hide()
        elif event.key()==Qt.Key_I:
            self.input.setFocus()
        elif event.modifiers():
            if event.key() in  [Qt.Key_L, Qt.Key_M, Qt.Key_Enter]:
                self.mode.confirmAction()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

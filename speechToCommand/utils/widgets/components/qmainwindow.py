import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import command

class MainWindow (QMainWindow):

    def __init__ (self, mode, window_title=''):
        super(MainWindow, self).__init__()
        self.mode=mode
        self.socket=mode.socket
        self.setWindowTitle(window_title)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def showAction(self, request={}):
        self.show()
        self.setFocus()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def hideAction(self, request={}):
        self.hide()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def doneAction(self, request={}):
        self.hide()

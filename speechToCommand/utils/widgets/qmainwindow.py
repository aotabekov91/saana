import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import command

class QBaseMainWindow (QMainWindow):

    def __init__ (self, mode, window_title=''):
        super(QBaseMainWindow, self).__init__()
        self.mode=mode
        self.socket=mode.socket
        self.setWindowTitle(window_title)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def move_to_center(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def showAction(self, request={}):
        self.show()
        self.setFocus()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def hideAction(self, request={}):
        self.hide()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def doneAction(self, request={}):
        self.hide()


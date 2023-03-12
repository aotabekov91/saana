import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class QBaseMainWindow (QMainWindow):

    def __init__ (self, app, window_title=''):
        super(QBaseMainWindow, self).__init__()
        self.app=app
        self.socket=app.socket
        self.setWindowTitle(window_title)

    def move_to_center(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.hide()
        else:
            super().keyPressEvent(event)

    def stop_waiting(self):
        self.app.stop_waiting()
    
    def showAction(self, request={}):
        self.show()
        self.setFocus()

    def hideAction(self, request={}):
        self.hide()

    def doneAction(self, request={}):
        self.hide()


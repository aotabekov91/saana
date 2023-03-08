from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class BaseMainWindow (QMainWindow):

    show_signal=pyqtSignal(dict)
    hide_signal=pyqtSignal(dict)
    done_signal=pyqtSignal(dict)
    remove_signal=pyqtSignal(dict)
    choose_signal=pyqtSignal(dict)
    confirm_signal=pyqtSignal(dict)
    open_signal=pyqtSignal(dict)

    def __init__ (self, window_title=''):
        super(BaseMainWindow, self).__init__()
        self.setWindowTitle(window_title)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.hide()
        else:
            super().keyPressEvent(event)

    def handleRequest(self, request):
        if request['command']=='GenericMode_showAction':
            self.showAction(request)
        elif request['command']=='GenericMode_chooseAction':
            self.chooseAction(request)
        elif request['command']=='GenericMode_hideAction':
            self.hideAction(request)
        elif request['command']=='GenericMode_doneAction':
            self.doneAction(request)
        elif request['command']=='GenericMode_removeAction':
            self.removeAction(request)
        elif request['command']=='GenericMode_confirmAction':
            self.confirmAction(request)
        elif request['command']=='GenericMode_openAction':
            self.openAction(request)
        elif request['command']=='GenericMode_moveDown':
            self.moveDown(request)
        elif request['command']=='GenericMode_moveUp':
            self.moveUp(request)

    def showAction(self, request={}):
        self.hide()
        self.show()
        self.show_signal.emit(request)

    def hideAction(self, request={}):
        self.hide()
        self.hide_signal.emit(request)

    def doneAction(self, request={}):
        self.edit.clear()
        self.hide()
        self.done_signal.emit(request)

    def removeAction(self, request={}):
        self.edit.clear()
        self.remove_signal.emit(request)

    def chooseAction(self, request={}):
        self.choose_signal.emit(request)

    def openAction(self, request={}):
        self.open_signal.emit(request)

    def confirmAction(self, request={}):
        self.confirm_signal.emit(request)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .qmainwindow import QBaseMainWindow

from speechToCommand.utils.helper import command

class InputMainWindow (QBaseMainWindow):

    returnPressed=pyqtSignal()

    def __init__ (self, mode, window_title='', label_title=''):
        super(InputMainWindow, self).__init__(mode, window_title)
        self.label_title=label_title
        self.set_ui()
        self.setStyleSheet(self.style_sheet)
        self.setCentralWidget()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def showAction(self, request={}):
        print(request)
        self.hide()
        self.show()
        self.edit.setFocus()

    def clearAction(self, request={}):
        self.ui.edit.clear()

    def set_ui(self):

        self.setGeometry(0, 0, 700, 0)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.style_sheet='''
            QWidget{
                font-size: 18px;
                color: white;
                border-width: 0px;
                border-radius: 0px;
                border-color: transparent;
                background-color: transparent;
                }
            QWidget#input{
                background-color: green;
                }
            QLineEdit{
                border-style: outset;
                }
                '''

        self.main=QWidget(objectName='input')
        self.main.adjustSize()

        self.label= QLabel()
        self.label.setText(self.label_title)

        self.edit=QLineEdit()

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(10,0,0,0)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)

        self.main.setLayout(allQHBoxLayout)

        self.edit.returnPressed.connect(self.returnPressed)
        self.returnPressed.connect(self.mode.confirmAction)
    
    def setCentralWidget(self):
        super().setCentralWidget(self.main)
        # self.move_to_center()

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

    @command(checkWindowType=False)
    def showAction(self, request={}):
        print(request)
        self.hide()
        self.show()
        self.edit.setFocus()

    def clearAction(self, request={}):
        self.ui.edit.clear()

    def set_ui(self):

        self.setGeometry(0, 0, 700, 0)

        self.style_sheet='''
            QWidget{
                font-size: 16px;
                color: white;
                border-width: 0px;
                border-radius: 10px;
                border-style: outset;
                border-color: rgba(0,0,0,0);
                background-color: rgba(0,0,0,0);
                }
           QWidget#input{
                color: green;
                background-color: green;
                }
                '''

        self.main=QWidget(objectName='input')
        self.main.setWindowFlags(Qt.FramelessWindowHint)
        self.main.adjustSize()

        self.label= QLabel()#objectName='inputLabel')
        self.label.setText(self.label_title)

        self.edit=QLineEdit()#objectName='inputEdit')

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(10,5,0,5)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)

        self.main.setLayout(allQHBoxLayout)

        self.edit.returnPressed.connect(self.mode.confirmAction)
        self.returnPressed.connect(lambda: self.mode.confirmAction({}))
    
    def setCentralWidget(self):
        super().setCentralWidget(self.main)
        # self.move_to_center()

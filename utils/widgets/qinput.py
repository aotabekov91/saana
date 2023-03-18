from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .qmainwindow import QBaseMainWindow

class InputMainWindow (QBaseMainWindow):

    returnPressed=pyqtSignal()

    def __init__ (self, app, window_title='', label_title=''):
        super(InputMainWindow, self).__init__(app, window_title)
        self.label_title=label_title
        self.set_ui()
        self.setStyleSheet(self.style_sheet)
        self.setCentralWidget()

    def set_ui(self):

        self.setGeometry(0, 0, 700, 100)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.style_sheet='''
            QWidget{
                font-size: 16px;
                color: white;
                border-width: 0px;
                border-radius: 0px;
                border-color: transparent;
                background-color: transparent;
                }
            QLineEdit{
                border-style: outset;
                }
                '''

        self.main=QWidget(objectName='input')
        self.label= QLabel()
        self.label.setText(self.label_title)

        self.edit=QLineEdit()

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(15,7,0,7)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)

        self.main.setLayout(allQHBoxLayout)

        self.edit.returnPressed.connect(self.returnPressed)
        self.returnPressed.connect(self.app.confirmAction)
    
    def setCentralWidget(self):
        super().setCentralWidget(self.main)
        self.move_to_center()

import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .components import MainWindow
from speechToCommand.utils.helper import command

class MessageMainWindow(MainWindow):

    message_hidden=pyqtSignal()

    def __init__ (self, mode, window_title='', label_title=''):

        super(MessageMainWindow, self).__init__(mode, window_title)

        self.pause=False

        self.setGeometry(0, 0, 500, 500)
        self.setMinimumSize(QSize(600, 400))

        self.style_sheet='''
            QWidget{
                font-size: 18px;
                color: white;
                border-width: 0px;
                border-radius: 0px;
                border-color: transparent;
                background-color: transparent;
                }
            QWidget#title{
                background-color: green;
                }
            QWidget#information{
                background-color: blue;
                }
            QWidget#detail{
                background-color: blue;
                }
                '''

        self.main = QWidget()

        self.title=QLabel(objectName='title')
        self.information=QLabel(objectName='information')
        self.detail=QLabel(objectName='detail')

        self.title.hide()
        self.title.setMargin(10)

        self.information.hide()
        self.information.setWordWrap(True)
        self.information.setMargin(10)

        self.detail.hide()
        self.detail.setWordWrap(True)
        self.detail.setMargin(10)

        layout=QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        layout.addWidget(self.title, 10)
        layout.addWidget(self.information, 50)
        layout.addWidget(self.detail, 40)
        layout.addStretch(1)

        self.main.setLayout(layout)
        self.main.adjustSize()

        self.setStyleSheet(self.style_sheet)
        self.setCentralWidget(self.main)

    def set_title(self, text):
        text=text.strip().title()
        self.title.setText(text)
        self.title.adjustSize()
        self.adjustSize()
        self.title.show()

    def set_detail(self, text):
        text=text.strip()
        self.detail.setText(text)
        self.detail.adjustSize()
        self.adjustSize()
        self.detail.show()

    def set_information(self, text):
        text=text.strip()
        self.information.setText(text)
        self.information.adjustSize()
        self.adjustSize()
        self.information.show()

    def set_timer(self, timeout):
        QTimer.singleShot(timeout, self.hide)

    def pauseAction(self, request={}):
        self.pause=True

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Escape:
            self.pause=False
            self.hide()
        elif event.key()==Qt.Key_Space:
            self.pause=True

    def hide(self):
        if not self.pause:
            super().hide()
            self.title.setText('')
            self.information.setText('')
            self.detail.setText('')
            self.message_hidden.emit()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def hideAction(self, request):
        self.pause=False
        self.hide()

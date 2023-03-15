import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .qbase import QBaseMainWindow

class InputMainWindow (QBaseMainWindow):

    returnPressed=pyqtSignal()

    def __init__ (self, app, window_title='', label_title=''):
        super(InputMainWindow, self).__init__(app, window_title)

        self.setGeometry(0, 0, 700, 10)

        self.info=QWidget()
        self.label= QLabel()
        self.label.setText(label_title)
        self.edit=QLineEdit()
        self.edit.returnPressed.connect(self.returnPressed)

        self.label.hide()

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(0,0,0,0)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)
        self.info.setLayout(allQHBoxLayout)

        self.setCentralWidget(self.info)

        self.edit.returnPressed.connect(self.returnPressed)
        self.returnPressed.connect(self.app.confirmAction)

        self.move_to_center()
        # self.adjustSize()

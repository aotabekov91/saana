from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

                # border-color: transparent;
                # border-style: outset;
                # border-width: 0px;
                # border-radius: 10px;

class EWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputWidget (QWidget):

    returnPressed=pyqtSignal()
    textChanged=pyqtSignal()

    def __init__ (self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 

        self.style_sheet='''
            QWidget{
                color: black;
                background-color: white;
                border-color: transparent;
                border-style: outset;
                border-width: 0px;
                border-radius: 10px;
                border-style: outset;
                }
                '''

        self.label= QLabel()
        ww=QWidget()
        layout=QVBoxLayout()
        layout.addWidget(self.label)
        ww.setLayout(layout)

        self.edit=QLineEdit()
        w=QWidget()
        layout=QVBoxLayout()
        layout.addWidget(self.edit)
        w.setLayout(layout)

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setSpacing(0)
        allQHBoxLayout.setContentsMargins(0,0,0,0)
        allQHBoxLayout.addWidget(ww, 10)
        allQHBoxLayout.addWidget(w, 90)

        s=QWidget(objectName='inputContainerInput')
        s.setLayout(allQHBoxLayout)

        layout=QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(s)

        self.setLayout(layout)
        self.setStyleSheet(self.style_sheet)

        self.edit.returnPressed.connect(self.returnPressed)
        self.edit.textChanged.connect(self.textChanged)

        self.adjustSize()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def label(self):
        return self.label.text()

    def setLabel(self, label):
        self.label.setText(label)
        self.label.setAlignment(Qt.AlignCenter)

    def text(self):
        return self.edit.text()

    def setText(self, text):
        self.edit.setText(text)

    def sizeHint(self):
        return QSize(700, 40)

    def clear(self):
        self.edit.clear()

    def setFocus(self):
        self.edit.setFocus()

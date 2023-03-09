from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .qbase import BaseMainWindow

class QCustomListItem (QWidget):
    def __init__ (self, parent = None):
        super(QCustomListItem, self).__init__(parent)

        self.textQVBoxLayout = QVBoxLayout()
        self.textQVBoxLayout.setSpacing(0)
        self.textUpQLabel    = QLabel()
        self.textUpQLabel.setWordWrap(True)
        self.textUpQLabel.setStyleSheet('''color: rgb(0, 0, 255);''')
        self.textDownQLabel  = QLabel()
        self.textDownQLabel.setWordWrap(True)
        self.textDownQLabel.setStyleSheet('''color: rgb(255, 0, 0);''')
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        # self.textQVBoxLayout.addStretch(1)

        self.allQHBoxLayout  = QHBoxLayout()
        self.allQHBoxLayout.setSpacing(5)
        self.textQVBoxLayout.setContentsMargins(4,2,2,4)
        self.iconQLabel      = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)

        self.textUpQLabel.hide()
        self.textDownQLabel.hide()
        self.iconQLabel.hide()

    def getTextDown(self):
        return self.textDownQLabel.text()

    def getTextUp(self):
        return self.textUpQLabel.text()

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)
        self.textDownQLabel.adjustSize()
        self.textDownQLabel.show()

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)
        self.textUpQLabel.adjustSize()
        self.textUpQLabel.show()

    def setIcon (self, imagePath):
        self.iconQLabel.path=imagePath
        self.iconQLabel.setPixmap(QPixmap(imagePath).scaled(50, 50, Qt.KeepAspectRatio))
        self.iconQLabel.adjustSize()
        self.iconQLabel.show()

    def getHintSize(self):
        upHint=self.textUpQLabel.sizeHint().height()
        downHint=self.textDownQLabel.sizeHint().height()
        iconHint=self.iconQLabel.sizeHint().height()
        hint_height=upHint+downHint+iconHint
        return QSize(600, hint_height)

class ListMainWindow (BaseMainWindow):

    def __init__ (self, window_title='', label_title=''):
        super(ListMainWindow, self).__init__(window_title)

        self.setGeometry(0, 0, 800, 600)

        self.info=QWidget()
        self.label= QLabel()
        self.label.setText(label_title)
        self.edit=QLineEdit()
        self.edit.textChanged.connect(self.inputTextChanged)
        self.label.hide()
        self.dlist=[]

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(0,5,0,0)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)
        self.info.setLayout(allQHBoxLayout)

        self.list = QListWidget()
        self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout=QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        layout.addWidget(self.info)
        layout.addWidget(self.list)

        self.main=QWidget()
        self.main.setLayout(layout)

        self.setCentralWidget(self.main)

    def adjustSize(self):
        heightHint=0
        for i in range(self.myQListWidget.count()):
            heightHint+=self.myQListWidget.sizeHintForRow(i)
        heightHint+=2*self.myQListWidget.frameWidth()
        if self.width()>heightHint:
            self.setGeometry(0,0,800,heightHint)

    def inputTextChanged(self, text):
        self.list.clear()
        dlist=[]
        for i, w in enumerate(self.dlist):
            text_up=w['top']
            text_down=w.get('down', '')
            if (text.lower() in text_up.lower() or text.lower() in text_down.lower()):
                dlist+=[w]
        self.addWidgetsToList(dlist, False)

    def addWidgetsToList(self, dList, save=True):
        if save: self.dlist=dList
        self.list.clear()
        for d in dList:
            self.addWidgetToList(d)
        self.list.setCurrentRow(0)

    def addWidgetToList(self, w):

        item = QListWidgetItem(self.list)
        widget=QCustomListItem()
        item.itemData=w

        widget.setTextUp(w['top'])
        if w.get('down', False):
            widget.setTextDown(w['down'])
            widget.textDownQLabel.show()
        if w.get('icon', False):
            widget.setIcon(w['icon'])
            widget.iconQLabel.show()

        item.setSizeHint(widget.getHintSize())
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)

    def doneAction(self, request={}):
        super().doneAction(request)
        self.list.clear()

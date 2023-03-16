import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .qmainwindow import QBaseMainWindow

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


class ListMainWindow (QBaseMainWindow):

    returnPressed=pyqtSignal()

    def __init__ (self, app, window_title='', label_title=''):
        super(ListMainWindow, self).__init__(app, window_title)


        self.setGeometry(0, 0, 700, 500)

        self.info=QWidget()
        self.label= QLabel()
        self.label.setText(label_title)
        self.edit=QLineEdit()
        self.edit.textChanged.connect(self.inputTextChanged)
        self.edit.returnPressed.connect(self.returnPressed)
        # self.edit.keyPressEvent=self.keyPressEvent

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

        self.edit.returnPressed.connect(self.returnPressed)
        self.returnPressed.connect(self.app.confirmAction)

        self.move_to_center()
        self.adjustSize()

    def adjustSize(self):
        pass

        # try:
        #     heightHint=self.list.sizeHintForRow(0)
        # except:
        #     heightHint=0
        # hint=heightHint*self.list.count()+4
        # # for i in range(
        #     # heightHint+=self.list.sizeHintForRow(i)
        # # heightHint+=2*self.list.frameWidth()
        # # if self.width()>heightHint:
        #     # self.setGeometry(0,0,800,heightHint)
        #     # self.setHeight(heightHint)
        # self.setMinimumHeight(hint)

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
        self.adjustSize()

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
        self.list.clear()
        self.edit.clear()
        self.hide()

    def chooseAction(self, request={}):
        slot_names=request['slot_names']
        item=slot_names.get('item', None)
        if item:
            self.edit.setText(item)
            self.show()
            self.setFocus()

    # def moveUpAction(self, request={}):
    #     crow=self.list.currentRow()
    #     if crow>0:
    #         crow-=1
    #         self.list.setCurrentRow(crow)

    # def moveDownAction(self, request={}):
    #     crow=self.list.currentRow()
    #     if crow-1<self.list.count():
    #         crow+=1
    #         self.list.setCurrentRow(crow)

    def showAction(self, request={}):
        self.list.show()
        self.show()
        self.edit.setFocus()

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Escape:
            self.hide()
        elif self.list.hasFocus():
            if event.key()==Qt.Key_J:
                self.moveDownAction()
            elif event.key()==Qt.Key_K:
                self.moveUpAction()
            elif event.key()==Qt.Key_L:
                self.returnPressed.emit()
        elif event.modifiers() and Qt.ControlModifier:
            if event.key() == Qt.Key_N:
                self.moveDownAction()
            elif event.key() == Qt.Key_P:
                self.moveUpAction()
            elif event.key() == Qt.Key_M:
                self.returnPressed.emit()
        elif self.edit.hasFocus():
            if event.key() in [Qt.Key_Down, Qt.Key_Up]:
                self.list.keyPressEvent(event)
            else:
                self.edit.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

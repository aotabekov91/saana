import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from playsound import playsound
from .qmainwindow import QBaseMainWindow

rest='''
    QLabel{
        color: white;
        background-color: gray;
        border-radius: 10px;
        border-width: 2px;
        }
    QLabel:focus{
        font: bold; 
        }
    QLineEdit {
        color: #ffffff;
        border-style: outset;
        border-radius: 10px;
        border-width: 2px;
        border-color: blue; 
        background-color: gray;
        border-color: #ffffff;
        }
    QListWidget{
        color: rgba(0,0,0,1.);
        background-color: rgba(0,0,0,1.);
        border-width: 0px;
        }
    QListWidget::item:selected {
        color: yellow;
        background-color: transparent;
        border-width: 3px;
        }
    QListWidget::item{
        background-color: transparent;
        border-style: outset;
        border-radius: 10px;
        border-width: 2px;
        }
        '''

class QCustomListItem (QWidget):
    def __init__ (self, parent = None):
        super(QCustomListItem, self).__init__(parent)

        self.textQVBoxLayout = QVBoxLayout()
        self.textQVBoxLayout.setSpacing(10)
        self.textQVBoxLayout.setContentsMargins(5,5,5,5)

        self.textUpQLabel    = QLabel()
        self.textUpQLabel.setWordWrap(True)
        self.textDownQLabel  = QLabel()
        self.textDownQLabel.setWordWrap(True)
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addStretch()
        self.textQVBoxLayout.addWidget(self.textDownQLabel)

        self.allQHBoxLayout  = QHBoxLayout()
        self.iconQLabel      = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)

        self.textUpQLabel.hide()
        self.textDownQLabel.hide()
        self.iconQLabel.hide()

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)
        self.textDownQLabel.adjustSize()
        self.textDownQLabel.show()

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)
        self.textDownQLabel.adjustSize()
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
        hint_height=upHint+downHint
        # return QSize(600, hint_height)
        return QSize(600, 70)


class ListMainWindow (QBaseMainWindow):

    returnPressed=pyqtSignal()

    def __init__ (self, app, window_title='', label_title=''):
        super(ListMainWindow, self).__init__(app, window_title)


        self.setGeometry(0, 0, 700, 500)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setStyleSheet('''
            QWidget{
                font-size: 20;
                color: white;
                border-width: 0px;
                border-radius: 0px;
                border-color: transparent;
                background-color: transparent;
                }
            QCustomListItem{
                background-color: transparent;
                }
            QLineEdit{
                border-style: outset;
                }
            QListWidget::item{
                color: transparent;
                background-color: tranparent;
                }
            QListWidget::item:selected {
                color: blue;
                background-color: blue;
                }
                '''
                           )


        self.info=QWidget()
        self.label= QLabel()
        self.label.setText(label_title)
        # self.label.hide()

        self.edit=QLineEdit()

        # font=self.edit.font()
        # font.setPointSize(16)
        # self.edit.setFont(font)

        self.dlist=[]

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(5,2,0,2)
        allQHBoxLayout.setSpacing(10)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)
        self.info.setLayout(allQHBoxLayout)

        self.list = QListWidget()
        self.list.setWordWrap(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout=QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.info)
        layout.addWidget(self.list)

        self.main=QWidget()
        self.main.setLayout(layout)

        self.main.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet('background-color: transparent; ')
        # self.main.setStyleSheet('background-color: transparent')
        self.main.setWindowFlags(Qt.FramelessWindowHint)
        self.main.setWindowOpacity(1.)
        self.list.setAttribute(Qt.WA_TranslucentBackground)
        self.list.setWindowFlags(Qt.FramelessWindowHint)
        self.list.setWindowOpacity(1.)

        self.setCentralWidget(self.main)

        self.edit.textChanged.connect(self.inputTextChanged)
        self.edit.returnPressed.connect(self.returnPressed)
        self.edit.returnPressed.connect(self.returnPressed)
        self.returnPressed.connect(self.app.confirmAction)

        self.move_to_center()

    def inputTextChanged(self, text):
        self.list.clear()
        dlist=[]
        for i, w in enumerate(self.dlist):
            text_up=w['top']
            text_down=w.get('down', '')
            if (text.lower() in text_up.lower() or text.lower() in text_down.lower()):
                dlist+=[w]
        self.addWidgetsToList(dlist, False)

    def sizeHint(self):
        hint=super().sizeHint()
        height=self.list.count()*70
        hint.setHeight(height)
        hint.setWidth(self.size().width())
        return hint

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

        widget.setTextDown(w.get('down', ''))

        if w.get('icon', False):
            widget.setIcon(w['icon'])
            widget.iconQLabel.show()

        item.setSizeHint(widget.getHintSize())
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)
        return widget

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

    def moveUpAction(self, request={}):
        crow=self.list.currentRow()
        if crow>0:
            crow-=1
            self.list.setCurrentRow(crow)

    def moveDownAction(self, request={}):
        crow=self.list.currentRow()
        if crow-1<self.list.count():
            crow+=1
            self.list.setCurrentRow(crow)

    def showAction(self, request={}):
        self.list.show()
        self.show()
        self.edit.setFocus()

    def soundAction(self, request):
        if self.isVisible():
            item=self.list.currentItem()
            if item:
                meta=request['slot_names'].get('meta', 'top')
                sound_path=item.itemData.get(f'sound_{meta}', None)
                if sound_path:
                    playsound(sound_path, block=False)

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

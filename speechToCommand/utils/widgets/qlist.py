import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from playsound import playsound
from .qinput import InputMainWindow
from speechToCommand.utils.helper import command

class QCustomListWidget(QListWidget):

    def sizeHint(self):

        hint=QSize(700, 0)
        if self.count()>0:
            item=self.item(0)
            item_height = item.sizeHint().height()
            total_height=self.count()*item_height
            if total_height > 500:
                total_height=(500//item_height)*item_height
            total_height+=hint.height()
            hint.setHeight(total_height)
        return hint

class QCustomListItem (QWidget):
    def __init__(self, parent=None):
        super(QCustomListItem, self).__init__(parent)

        self.textQVBoxLayout = QVBoxLayout()
        self.textQVBoxLayout.setSpacing(0)
        self.textQVBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.textUpQLabel = QLabel()
        self.textUpQLabel.setWordWrap(True)
        self.textDownQLabel = QLabel()
        self.textDownQLabel.setWordWrap(True)
        self.textQVBoxLayout.addWidget(self.textUpQLabel, 50)
        self.textQVBoxLayout.addWidget(self.textDownQLabel, 50)

        self.allQHBoxLayout = QHBoxLayout()
        self.iconQLabel = QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 30)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 70)
        self.setLayout(self.allQHBoxLayout)

        self.textUpQLabel.hide()
        self.textDownQLabel.hide()
        self.iconQLabel.hide()

    def setTextDown(self, text):
        self.textDownQLabel.setText(text)
        self.textDownQLabel.adjustSize()
        self.textDownQLabel.show()

    def setTextUp(self, text):
        self.textUpQLabel.setText(text)
        self.textDownQLabel.adjustSize()
        self.textUpQLabel.show()

    def setIcon(self, imagePath):
        self.iconQLabel.path = imagePath
        self.iconQLabel.setPixmap(
            QPixmap(imagePath).scaled(50, 50, Qt.KeepAspectRatio))
        self.iconQLabel.adjustSize()
        self.iconQLabel.show()


class ListMainWindow (InputMainWindow):

    def __init__(self, mode, window_title='', label_title=''):
        super(ListMainWindow, self).__init__(
            mode, window_title, label_title=label_title)

        self.dlist = []

    def set_ui(self):

        super().set_ui()

        self.info = self.main
        self.setGeometry(0, 0, 700, 500)

        self.style_sheet += '''
            QListWidget::item{
                color: transparent;
                background-color: transparent;
                }
            QListWidget::item:selected {
                color: blue;
                background-color: blue;
                }
                '''

        self.list = QCustomListWidget() 
        self.list.setWordWrap(True)
        self.list.setSpacing(0)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.info)
        layout.addWidget(self.list)

        self.main = QWidget()
        self.main.setLayout(layout)

        self.edit.textChanged.connect(self.inputTextChanged)

    def inputTextChanged(self, text):
        self.list.clear()
        dlist = []
        for i, w in enumerate(self.dlist):
            text_up = w['top']
            text_down = w.get('down', '')
            if (text.lower() in text_up.lower() or text.lower() in text_down.lower()):
                dlist += [w]
        self.addWidgetsToList(dlist, False)

    def sizeHint(self):

        hint=self.info.sizeHint()
        if self.list.count()>0:
            list_hint=self.list.sizeHint()
            hint=QSize(700, hint.height()+list_hint.height())
        return hint

    def addWidgetsToList(self, dList, save=True):
        self.list.clear()
        if save: self.dlist = dList
        if len(dList)==0: dList=[{'top': 'No matches are found'}]
        widgets=[]
        for d in dList:
            widgets+=[self.addWidgetToList(d)]
        width=self.size().width()
        height=0
        for i, w in enumerate(widgets):
            if w.sizeHint().height()>height:
                height=w.sizeHint().height()
        hint=QSize(width, height)
        for i in range(len(widgets)):
            item=self.list.item(i)
            item.setSizeHint(hint)
        self.list.setCurrentRow(0)

        self.adjustSize()

    def addWidgetToList(self, w):

        item = QListWidgetItem(self.list)
        widget = QCustomListItem()
        item.itemData = w

        widget.setTextUp(w['top'])

        widget.setTextDown(w.get('down', ''))

        if w.get('icon', False):
            widget.setIcon(w['icon'])
            widget.iconQLabel.show()

        self.list.addItem(item)
        self.list.setItemWidget(item, widget)
        return widget

    @command(checkActionOnFinish=True, checkWindowType=False)
    def doneAction(self, request={}):
        self.list.clear()
        self.edit.clear()
        self.hide()

    def chooseAction(self, request={}):
        slot_names = request['slot_names']
        item = slot_names.get('item', None)
        if item:
            self.edit.setText(item)
            self.show()
            self.setFocus()

    def moveAction(self, request={}, crement=-1):
        crow = self.list.currentRow()
        if crow==None: return
        crow += crement
        if crow < 0:
            crow = self.list.count()-1
        elif crow >= self.list.count():
            crow = 0
        self.list.setCurrentRow(crow)

    def showAction(self, request={}):
        self.hide()
        self.list.show()
        self.show()
        self.edit.setFocus()

    def soundAction(self, request):
        if self.isVisible():
            item = self.list.currentItem()
            if item:
                meta = request['slot_names'].get('meta', 'top')
                sound_path = item.itemData.get(f'sound_{meta}', None)
                if sound_path:
                    playsound(sound_path, block=False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.modifiers() and Qt.ControlModifier:
            if event.key() in [Qt.Key_J, Qt.Key_N]:
                self.moveAction(crement=1)
            elif event.key() in [Qt.Key_K, Qt.Key_P]:
                self.moveAction(crement=-1)
            elif event.key() in  [Qt.Key_L, Qt.Key_M]:
                self.returnPressed.emit()
        elif self.edit.hasFocus():
            if event.key() in [Qt.Key_Down, Qt.Key_Up]:
                self.list.keyPressEvent(event)
            else:
                self.edit.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

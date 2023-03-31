from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.helper import command
from .components import MainWindow, InputWidget
from .components import CustomListWidget, CustomListItem

class ListWindow (MainWindow):

    returnPressed=pyqtSignal()
    inputTextChanged=pyqtSignal()

    def __init__(self, mode, window_title='', label_title=''):
        super(ListWindow, self).__init__(mode, window_title)

        self.style_sheet='''
            QWidget{
                font-size: 16px;
                color: black;
                border-width: 0px;
                background-color: grey; 
                border-color: transparent;
                }
            QWidget#mainWidget{
                border-radius: 10px;
                border-style: outset;
                background-color: transparent; 
                }
                '''
        

        self.dlist = []

        self.input=InputWidget(self, objectName='inputContainerInput') 
        self.input.setLabel(label_title)

        self.list=CustomListWidget(self)

        self.setGeometry(0, 0, 700, 500)

        self.main=QWidget(objectName='mainWidget')
        self.main.setStyleSheet(self.style_sheet)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.input)
        layout.addWidget(self.list)

        self.main.setLayout(layout)
        self.setCentralWidget(self.main)

        self.input.returnPressed.connect(self.returnPressed)
        self.input.textChanged.connect(self.inputTextChanged)
        self.input.textChanged.connect(self.onInputTextChanged)

    def onInputTextChanged(self):
        text=self.input.text()
        self.list.clear()
        dlist = []
        for i, w in enumerate(self.dlist):
            text_up = w['top']
            text_down = w.get('down', '')
            if (text.lower() in text_up.lower() or text.lower() in text_down.lower()):
                dlist += [w]
        self.addWidgetsToList(dlist, False)

    def sizeHint(self):
        hint=self.input.sizeHint()
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
        widget = CustomListItem()
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
        self.input.clear()
        self.hide()

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
        self.input.setFocus()

    def setFocus(self):
        self.input.setFocus()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Down, Qt.Key_Up]:
            self.list.keyPressEvent(event)
        elif event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.hide()
        elif event.key()==Qt.Key_I:
            self.input.setFocus()
        elif event.modifiers() or self.list.hasFocus():
            if event.key() in [Qt.Key_J, Qt.Key_N]:
                self.moveAction(crement=1)
            elif event.key() in [Qt.Key_K, Qt.Key_P]:
                self.moveAction(crement=-1)
            elif event.key() in  [Qt.Key_L, Qt.Key_M, Qt.Key_Enter]:
                self.mode.confirmAction()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def setText(self, text):
        self.input.setText(text)
    
    def text(self):
        return self.input.text()

    def setLabel(self, text):
        self.input.setLabel(text)

    def label(self):
        self.input.label()

    def clear(self):
        self.input.clear()

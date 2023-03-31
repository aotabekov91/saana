from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class CustomListWidget(QListWidget):

    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)

        self.style_sheet = '''
            QListWidget{
                border-width: 0px;
                color: transparent;
                border-color: transparent; 
                background-color: transparent; 
                }
            QListWidget::item{
                border-style: outset;
                border-width: 0px;
                border-radius: 10px;
                border-style: outset;
                color: transparent;
                border-color: transparent;
                background-color: transparent; 
                }
            QListWidget::item:selected {
                border-width: 2px;
                border-color: red;
                }
                '''

        self.setWordWrap(True)
        self.setSpacing(0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.adjustSize()
        self.setStyleSheet(self.style_sheet)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

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

class CustomListItem (QWidget):
    def __init__(self, parent=None):
        super(CustomListItem, self).__init__(parent)

        self.style_sheet = '''
            QWidget#containerListItemWidget{
                border-style: outset;
                border-width: 0px;
                border-radius: 10px;
                color: transparent;
                background-color: transparent;
                }
            QWidget#text{
                border-style: outset;
                border-width: 0px;
                border-radius: 10px;
                color: transparent;
                }
            QLabel{
                padding: 0 0 0 10px;
                }
                '''

        self.textQVBoxLayout = QVBoxLayout()
        self.textQVBoxLayout.setSpacing(0)
        self.textQVBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.textUpQLabel = QLabel()
        self.textUpQLabel.setWordWrap(True)
        self.textDownQLabel = QLabel()
        self.textDownQLabel.setWordWrap(True)
        self.textQVBoxLayout.addWidget(self.textUpQLabel, 50)
        self.textQVBoxLayout.addWidget(self.textDownQLabel, 50)

        t=QWidget(objectName='test')
        t.setLayout(self.textQVBoxLayout)
        t.setStyleSheet(self.style_sheet)

        self.iconQLabel = QLabel()

        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.addWidget(self.iconQLabel)
        self.allQHBoxLayout.addWidget(t)

        s=QWidget(objectName='containerListItemWidget')
        s.setStyleSheet(self.style_sheet)
        s.setLayout(self.allQHBoxLayout)
        
        layout=QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(s)

        self.setLayout(layout)

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
        # self.iconQLabel.adjustSize()
        self.iconQLabel.setFixedWidth(int(0.25*self.size().width()))
        self.iconQLabel.show()

import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode

class NotifyMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(NotifyMode, self).__init__(
                 keyword='notify', 
                 info='Notifier', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.msgBox = QMessageBox()
        self.msgBox.setGeometry(0, 0, 400, 200)
        # self.moveToCenter()

    def notifyAction(self, request):
        slot_names=request['slot_names']
        text=slot_names.get('text', '')
        detail=slot_names.get('detail', '')
        timeout=slot_names.get('timeout', 5000)
        self.msgBox.setText(text)
        self.msgBox.setInformativeText(detail)
        self.msgBox.show()
        QTimer.singleShot(timeout, self.msgBox.hide)

    def moveToCenter(self):
        screenGeometry = QApplication.desktop().availableGeometry()
        screenGeo = screenGeometry.bottomRight()
        msgGeo = QRect(QPoint(0,0), QSize(300, 200)) 
        msgGeo.moveTopRight(screenGeo)
        self.msgBox.move(msgGeo.topLeft())

if __name__=='__main__':
    app=NotifyMode(port=33333)
    app.run()

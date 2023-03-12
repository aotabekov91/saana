import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from .qbase import QBaseMainWindow

class Browser(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Title</title>
                <meta charset="utf-8" />
            </head>
            <body>
                <p>{}</p>
            </body>
        </html>
        """

    def loadHtml(self, html):
        here = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        base_path = os.path.join(os.path.dirname(here), 'dummy').replace('\\', '/')
        self.url = QUrl('file:///' + base_path)
        self.page().setHtml(html, baseUrl=self.url)

class RenderMainWindow (QBaseMainWindow):
    def __init__ (self, app, window_title='', label_title=''):
        super(RenderMainWindow, self).__init__(app, window_title)

        self.setGeometry(0, 0, 800, 600)

        self.info=QWidget()
        self.label= QLabel()
        self.label.setText(label_title)
        self.edit=QLineEdit()
        if label_title=='': self.label.hide()

        allQHBoxLayout  = QHBoxLayout()
        allQHBoxLayout.setContentsMargins(0,5,0,0)
        allQHBoxLayout.addWidget(self.label, 0)
        allQHBoxLayout.addWidget(self.edit, 0)
        self.info.setLayout(allQHBoxLayout)

        self.browser = Browser()

        layout=QVBoxLayout()
        layout.setContentsMargins(5,0,5,5)
        layout.setSpacing(0)
        layout.addWidget(self.info, 7)
        layout.addWidget(self.browser, 93)

        self.main=QWidget()
        self.main.setLayout(layout)

        self.setCentralWidget(self.main)

        self.edit.returnPressed.connect(self.app.confirmAction)

    def chooseAction(self, request={}):
        slot_names=request['slot_names']
        text=slot_names.get('item', '')
        self.edit.setText(text)
        self.show()
        self.edit.setFocus()

    def doneAction(self, request):
        self.edit.clear()
        self.browser.setHtml('')
        self.hide()

    def showAction(self, request):
        self.show()
        self.browser.show()
        self.edit.setFocus()

    def set_html(self, html):
        self.browser.setHtml(html)
        # self.browser.loadHtml(html)

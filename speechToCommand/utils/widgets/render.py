import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from .components import InputWidget, MainWindow
from speechToCommand.utils.helper import command

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
        self.page().setHtml(html)#, baseUrl=self.url)

    def loadCSS(self, path, name='css'):
        path = QFile(path)
        if not path.open(QFile.ReadOnly | QFile.Text):
            return
        css = path.readAll().data().decode("utf-8")

        SCRIPT = """
        (function() {
        css = document.createElement('style');
        css.type = 'text/css';
        css.id = "%s";
        document.head.appendChild(css);
        css.innerText = `%s`;
        })()
        """ % (name, css)

        script = QWebEngineScript()
        self.page().runJavaScript(
                SCRIPT, QWebEngineScript.ApplicationWorld)
        script.setName(name)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        self.page().scripts().insert(script)

class RenderWindow (MainWindow):

    returnPressed=pyqtSignal()
    inputTextChanged=pyqtSignal()

    def __init__ (self, mode, window_title='', label_title=''):
        super(RenderWindow, self).__init__(mode, window_title)

        self.waiting=False

        self.style_sheet='''
            QWidget{
                font-size: 16px;
                color: black;
                background-color: transparent; 
                border-width: 0px;
                border-radius: 0px;
                }
            QWidget#browserContainer{
                border-color: red;
                border-width: 2px;
                border-radius: 10px;
                border-style: outset;
                }
                '''

        self.input=InputWidget()
        self.input.setLabel(label_title)
        self.browser = Browser()

        w=QWidget(objectName='browserContainer')
        layout=QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(7,7,7,7)
        layout.addWidget(self.browser)
        w.setLayout(layout)
        w.setStyleSheet(self.style_sheet)

        self.setGeometry(0, 0, 700, 100)

        layout=QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0,0,0,0)

        self.setFixedSize(QSize(700, 500))

        layout.addWidget(self.input)
        layout.addWidget(w)

        self.main=QWidget(objectName='container')
        self.main.setLayout(layout)

        self.main.setStyleSheet(self.style_sheet)

        self.setCentralWidget(self.main)

        self.input.returnPressed.connect(self.returnPressed)
        self.input.textChanged.connect(self.inputTextChanged)

    @command(checkActionOnFinish=True, checkWindowType=False)
    def doneAction(self, request):
        self.input.clear()
        self.browser.setHtml('')
        self.hide()

    @command(checkActionOnFinish=True, checkWindowType=False)
    def showAction(self, request):
        self.hide()
        self.show()
        self.browser.show()
        self.input.setFocus()

    def set_css(self, css):
        self.browser.loadCSS(css)

    def set_html(self, html):
        self.browser.loadHtml(html)

    def text(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText()

    def clear(self):
        self.input.clear()

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

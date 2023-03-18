import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from .qinput import InputMainWindow

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

class RenderMainWindow (InputMainWindow):
    def __init__ (self, app, window_title='', label_title=''):
        super(RenderMainWindow, self).__init__(app, window_title, label_title)

    def set_ui(self):

        super().set_ui()
        self.info=self.main
        self.setGeometry(0, 0, 700, 100)

        self.browser = Browser()

        self.style_sheet += '''
            QWebEngineView{
                color: transparent;
                background-color: black;
                }
                '''

        layout=QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        # layout.addWidget(self.info)
        # layout.addWidget(self.browser)

        layout.addWidget(self.info, 10)
        layout.addWidget(self.browser, 90)

        self.main=QWidget()
        self.main.setLayout(layout)

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

    def set_css(self, css):
        self.browser.loadCSS(css)

    def set_html(self, html):
        # self.browser.setHtml(html)
        self.browser.loadHtml(html)

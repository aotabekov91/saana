import os
import time
import openai

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qrender import RenderMainWindow 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class AIAnswer(QObject):
    
    answered=pyqtSignal(str, str)

    def __init__(self, parent):
        self.parent=parent
        self.question=None

    def loop(self):
        self.running=True

        while self.running:
            if self.question:
                answer=self.get_answer(self.question)
                self.answered.emit(self.question, answer)
            self.question=None
            time.sleep(1)

    def get_answer(self, question):
        openai.api_key=os.environ['OPEN_AI_API']
        try:
            r=openai.Completion.create(
                model='text-davinci-003',
                prompt=question,
                temperature=0.5,
                top_p=0.1,
                max_tokens=100)
            return r['choices'][0]['text']
        except:
            return ''

class AIMode(QBaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(AIMode, self).__init__(
                 keyword='question', 
                 info='AIMode', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)


        self.ui=RenderMainWindow(self, 'OpenAI - own_floating', 'Question: ')
        self.ui.edit.textChanged.connect(self.uiEditTextChanged)
        self.set_answerer()

    def set_answerer(self):
        self.answerer=AIAnswer(self)
        self.answer_thread=QThread()
        self.answerer.moveToThread(self.answer_thread)
        self.answerer.answered.connect(self.update)
        self.answer_thread.started.connect(self.answerer.loop)
        QTimer.singleShot(0, self.answer_thread.start)

    @pyqtSlot(str, str)
    def update(self, question, answer):
        html=self.getHtml(question, answer)
        self.ui.setHtml(html)
        self.ui.show()

    def confirmAction(self, request=None):
        question=self.ui.edit.text()
        self.answerer.question=question
        html=self.getHtml(question, 'Waiting...')
        self.ui.setHtml(html)

    def uiEditTextChanged(self, text):
        html=self.getHtml(text, '')
        self.ui.setHtml(html)

    def getHtml(self, question, answer):
        html='''
        <!doctype html>
            <html>
                <head>
                    <title>Our Funky HTML Page</title>
                    <meta name="description" content="Our first page">
                    <meta name="keywords" content="html tutorial template">
                </head>
                <body>
                    <p>{}</p>
                    <p>{}</p>
                </body>
        </html>
        '''.format(question, answer)
        return html

if __name__=='__main__':
    app=AIMode(port=3333)
    app.run()

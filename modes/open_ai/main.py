import os
import sys
import time
import openai

from tendo import singleton

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseGenericMode
from speechToCommand.utils.widgets.qrender import RenderMainWindow 


class AIAnswer(QObject):
    
    answered=pyqtSignal(str, str)

    def __init__(self, parent):
        super(AIAnswer, self).__init__()
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

class AIMode(QBaseGenericMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(AIMode, self).__init__(
                 keyword='question', 
                 info='AIMode', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 argv=sys.argv)

        self.set_answerer()

        self.ui=RenderMainWindow(self, 'OpenAI - own_floating', 'Question: ')
        self.ui.set_css(self.css_path)
        self.ui.set_html(self.get_html())

    def hideAction(self, request={}):
        self.ui.hide()

    def set_answerer(self):
        self.answerer=AIAnswer(self)
        self.answer_thread=QThread()
        self.answerer.moveToThread(self.answer_thread)
        self.answerer.answered.connect(self.update)
        self.answer_thread.started.connect(self.answerer.loop)
        QTimer.singleShot(0, self.answer_thread.start)

    def set_config(self):
        super().set_config()
        main_path=self.get_mode_folder()
        self.css_path=f'{main_path}/{self.config.get("Custom", "css_path")}'

    @pyqtSlot(str, str)
    def update(self, question, answer):
        html=self.get_html(answer)
        self.ui.set_html(html)
        self.ui.show()

    def confirmAction(self, request=None):
        question=self.ui.edit.text()
        self.answerer.question=question
        html=self.get_html(' ... ')
        self.ui.set_html(html)

    def get_html(self, answer=''):
        html='''
        <!doctype html>
            <html>
                <head>
                    <title>OpenAI</title>
                </head>
                <body>
                    <p>Answer: {}</p>
                </body>
        </html>
        '''.format(answer)
        return html

if __name__=='__main__':
    app=AIMode()
    app.run()

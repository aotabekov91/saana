import os
import sys
import time
import threading

import openai

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import GenericMode
from speechToCommand.utils.widgets import RenderWindow 


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
                max_tokens=1000)
            return r['choices'][0]['text']
        except:
            return 'Could not fetch an answer from OPENAI'

class AIMode(GenericMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(AIMode, self).__init__(
                 keyword='a i', 
                 info='AIMode', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.set_answerer()

        self.question=None
        self.answer=None

        self.ui=RenderWindow(self, 'OpenAI - own_floating', 'Question: ')
        self.ui.returnPressed.connect(self.confirmAction)
        self.ui.inputTextChanged.connect(self.inputTextChanged)
        self.ui.set_css(self.css_path)
        self.ui.set_html(self.get_html())

    def hideAction(self, request={}):
        self.ui.hide()

    def copyAction(self, request):
        if self.answer and self.parent_port:
            self.parent_socket.send_json({
                'command': 'setModeAction',
                'mode_name': 'ClipboardMode', 
                'mode_action': 'saveToClipboardAction', 
                'slot_names': {'text':f'Question: \n{self.question}\nAnswer: {self.answer}'},
                })
            respond=self.parent_socket.recv_json()
            print(respond)
        self.client=None

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
        self.answer=answer
        answer=answer.replace('\n', '<br>')
        html=self.get_html(answer=answer, question=self.question)
        self.ui.set_html(html)
        self.ui.show()

    def inputTextChanged(self):
        self.question=self.ui.text()
        html=self.get_html(question=self.question)
        self.ui.set_html(html)

    def confirmAction(self, request={}):
        self.question=self.ui.text()
        self.answerer.question=self.question
        html=self.get_html(self.question, ' ... ')
        self.ui.set_html(html)

    def get_html(self, question='', answer='', badge=''):
        html='''
        <!doctype html>
            <html>
                <head>
                    <title>OpenAI</title>
                </head>
                <body>
                    <p>Question: {}</p>
                    <p>Answer: {} </p>
                    <p>{}</p>
                </body>
        </html>
        '''.format(question, badge, answer)
        return html

if __name__=='__main__':
    app=AIMode()
    app.ui.showAction({})
    app.run()

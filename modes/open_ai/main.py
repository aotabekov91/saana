import os
import openai

from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qrender import RenderMainWindow 

class AIMode(Mode):

    def __init__(self, config):

        super(AIMode, self).__init__(config, keyword='question', info='OpenAI')
        self.ui=RenderMainWindow('OpenAI - own_floating', 'Question: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.ui.edit.textChanged.connect(self.uiEditTextChanged)
        self.ui.confirm_signal.connect(self.confirmAction)

    def handleRequest(self, request):
        print(request)
        if request['command']=='AIMode_answerQuestion':
            _, __, ___, slots=self.parse_request(request)
            request=''
            if slots: request=slots[0]['value']['value']
            self.ui.edit.setText(request)
            self.ui.show()
        else:
            super().handleRequest(request)

    def confirmAction(self, request=None):
        question=self.ui.edit.text()
        ai_answer=self.get_answer(question)
        html=self.getHtml(question, ai_answer)
        self.ui.setHtml(html)
        self.ui.show()

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

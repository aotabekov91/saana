import sys

from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.window import BaseWindow

class AnkiMode(Mode):
    def __init__(self, config):
        super(AnkiMode, self).__init__(config, keyword='cards')
        self.ui=BaseWindow()

    def set_answer(self, answer_kind):
        print(answer_kind)

    def chooseAction(self, request):
        print(f'{self.__class__.__name__}: {request}')
        _, __, ___, slots=self.parse_request(request)
        if not slots: return
        answer_kind=slots[0]['value']['value']
        self.set_answer(answer_kind)

if __name__=='__main__':
    app=AnkiMode({'port':8234})
    sys.exit(app.exec_())

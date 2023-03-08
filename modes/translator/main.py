import sys
from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qlist import ListMainWindow
from googletrans import Translator as GTranslator

class TranslatorMode(Mode):
    def __init__(self, config):

        super(TranslatorMode, self).__init__(config, keyword='translator', info='Translator')
        self.translator=GTranslator()
        self.ui=ListMainWindow('Trans - own_floating', 'To translate: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.ui.confirm_signal.connect(self.confirmAction)
        self.ui.done_signal.connect(self.doneAction)

    def handleRequest(self, request):
        print(request)
        if request['command']=='TranslatorMode_translateAction':
            _, __, ___, slots=self.parse_request(request)
            if not slots: return
            request=slots[-1]['value']['value']
            self.ui.edit.setText(request)
            self.ui.show()
        else:
            super().handleRequest(request)

    def confirmAction(self, request={}):
        text=self.ui.edit.text()
        translation=self.translator.translate(text, dest='de').text
        self.ui.addWidgetsToList([{'top':self.ui.edit.text(), 'down':translation}])

    def doneAction(self, request={}):
        self.ui.list.clear()

if __name__ == '__main__':
    app = TranslatorMode({})
    app.ui.show()
    sys.exit(app.exec_())

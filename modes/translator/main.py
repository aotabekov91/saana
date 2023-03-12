import sys
from googletrans import Translator as GTranslator

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

import textwrap
import sys
import re

if (sys.version_info[0] < 3):
    import urllib2
    import urllib
    import HTMLParser
else:
    import html
    import urllib.request
    import urllib.parse

agent = {'User-Agent': "Mozilla/5.0 (Android 9; Mobile; rv:67.0.3) Gecko/67.0.3 Firefox/67.0.3"}

def translate(to_translate, to_language="auto", from_language="auto", wrap_len="80"):
    base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
    if (sys.version_info[0] < 3):
        to_translate = urllib.quote_plus(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib2.Request(link, headers=agent)
        raw_data = urllib2.urlopen(request).read()
    else:
        to_translate = urllib.parse.quote(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib.request.Request(link, headers=agent)
        raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="result-container">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) == 0):
        result = ""
    else:
        result = re_result[0]
    return ("\n".join(textwrap.wrap(result, int(wrap_len) if wrap_len.isdigit() else 80 )))

class TranslatorMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(TranslatorMode, self).__init__(
                 keyword='translator', 
                 info='Translator', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.ui=ListMainWindow(self, 'Translator - own_floating', 'Apps: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)

        self.to_lan='de'

    def setLanguageAction(self, request={}):
        slot_names=request['slot_names']
        self.to_lan=slot_names.get('lan', 'en')

    def confirmAction(self, request={}):
        text=self.ui.edit.text()
        trans=translate(text, self.to_lan)
        dlist=[{'top':text, 'down':trans}]
        self.ui.addWidgetsToList(dlist)
        self.ui.show()
        self.ui.setFocus()

if __name__=='__main__':
    app=TranslatorMode(port=33333)
    app.run()

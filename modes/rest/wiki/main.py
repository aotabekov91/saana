import os
import re
import sys

from subprocess import Popen

from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class WikiMode(Mode):
    def __init__(self, config):
        super(WikiMode, self).__init__(config, keyword='archive')
        self.mode=None
        self.set_folders()

        self.ui=ListMainWindow('Vimwiktionary - own_floating', 'Wiki: ')
        self.ui.returnPressed.connect(self.confirmAction)

    def showAction(self, request={}):
        self.mode='wiki'
        if not hasattr(self, 'dList'):
            self.dlist=self.get_wiki_data()
            self.ui.addWidgetsToList(self.dlist)
        self.ui.show()

    def set_folders(self):
        self.wiki_folder=os.path.expanduser('~/sciebo/vimwiki')
        self.diary_folder=os.path.expanduser('~/sciebo/vimwiki/work/diary/')
        if self.config.get('wiki_folder'):
            wiki=str(self.config.get('wiki_folder'))
            self.wiki_folder=os.path.expanduser(wiki)
        if self.config.get('dairy_folder'):
            diary=str(self.config.get('dairy_folder'))
            self.dairy_folder=os.path.expanduser(diary)

    def setDoneTodo(self):
        pass

    def handleRequest(self, request):
        if request['command']=='WikiMode_showTodos':
            self.mode='todo'
            self.dlist=self.get_todo_data()
            self.ui.addWidgetsToList(self.dlist)
            self.ui.show()
        else:
            super().handleRequest(request)

    def chooseAction(self, request={}):
        _, __, ___, slots=self.parse_request(request)
        app_name=''
        if slots: app_name=slots[0]['value']['value']

        if self.mode=='wiki':
            self.dlist=self.get_wiki_data()
        elif self.mode=='todo':
            self.dlist=self.get_todo_data()
        else:
            return
        self.ui.addWidgetsToList(self.dlist)
        self.ui.edit.setText(app_name)
        self.ui.show()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        line=item.itemData['line']
        path=item.itemData['path']

        os_cmd=['kitty', '--class', 'floating', 'vim', '-c Goyo', f'+{line}', path]
        Popen(os_cmd)

        self.ui.edit.clear()
        self.ui.hide()

    def get_wiki_data(self, wiki_folder=None, lines=None):
        lines=[]
        def run(wiki_folder, lines):
            if os.path.isfile(wiki_folder):
                if not wiki_folder.split('/')[-1].startswith('.'):
                    title=wiki_folder.split('vimwiki/')[-1]
                    title=title.replace('/', '>').split('.')[0]
                    if title.startswith('>'): title=title[1:]
                    lines+=[{'path':wiki_folder,
                             'top':title, 
                             'line':0,}
                            ]
            else:
                for d in os.listdir(wiki_folder):
                    run(f'{wiki_folder}/{d}', lines)
            return lines
        return run(self.wiki_folder, lines)

    def get_todo_data(self):

        todos=[]
        for d in os.listdir(self.diary_folder):
            with open(self.diary_folder+d, 'r') as f:
                lines=f.readlines()
                for i, line in enumerate(lines):
                    if not re.match('.*\[[^x]\].*', line): continue
                    line=re.sub('^[^[]*', '', line)
                    data={}
                    data['top']=line.strip('\n')
                    data['line']=i+1
                    data['path']=self.diary_folder+d
                    todos+=[data]
        return sorted(todos, key=lambda x: x['path'])

if __name__=='__main__':
    app=WikiMode({'port':8234})
    app.dlist=app.get_windows_data()
    app.ui.addWidgetsToList(app.dlist)
    app.ui.show()
    sys.exit(app.exec_())

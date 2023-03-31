import os
import re
import sys

import fileinput

from subprocess import Popen

from speechToCommand.utils.moder import GenericMode
from speechToCommand.utils.widgets import ListWindow

class WikiMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(WikiMode, self).__init__(
                 keyword='wiki', 
                 info='Wikis', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.mode=None
        self.ui=ListWindow(self, 'Vimwiktionary - own_floating', 'Wiki: ')
        self.ui.returnPressed.connect(self.confirmAction)

    def set_config(self):
        super().set_config()
        wiki=self.config.get('Custom', 'wiki_folder')
        self.wiki_folder=os.path.expanduser(wiki)
        diary=self.config.get('Custom', 'diary_folder')
        self.diary_folder=os.path.expanduser(diary)

    def finishAction(self, request={}):
        if self.ui.isVisible() and self.mode=='todos':
            item=self.ui.list.currentItem()
            line=item.itemData['line']
            path=item.itemData['path']

            data=[]
            for l in fileinput.input(path, inplace=True):
                data+=[(fileinput.filelineno(), l, type(l))]
                l=l.strip('\n')
                if item.itemData['top'] in l:
                    new_line=l.replace('[ ]', '[x]')
                    print(new_line)
                else:
                    print(l)
            print(line, item.itemData['top'], data)
            self.showTodos()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        line=item.itemData['line']
        path=item.itemData['path']
        os_cmd=['kitty', '--class', 'floating', 'vim', '-c',  'Goyo', f'+{line}', path]
        p=Popen(os_cmd)
        self.ui.clear()
        self.ui.hide()

    def showAction(self, request={}):
        if self.mode in ['wikis', None]:
            self.dlist=self.get_wiki_data()
        elif self.mode=='todos':
            self.dlist=self.get_todo_data()
        self.ui.addWidgetsToList(self.dlist)
        self.ui.show()
        self.ui.setFocus()
        self.changeModeAction(mode_name='me')

    def showTodos(self, request={}): 
        self.mode='todos'
        self.showAction(request)

    def showWikis(self, request={}): 
        self.mode='wikis'
        self.showAction(request)

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
    app=WikiMode(port=8234)
    app.run()

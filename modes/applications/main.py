import sys
import asyncio
import subprocess
from i3ipc.aio import Connection

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class ApplicationsMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ApplicationsMode, self).__init__(
                 keyword='applications', 
                 info='Applications', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.manager=asyncio.run(Connection().connect())

        self.ui=ListMainWindow(self, 'AppsMode - own_floating', 'Apps: ')

    def chooseAction(self, request={}):
        if self.ui.isVisible():
            app_name=request['slot_names'].get('app', '')
            dlist=self.get_windows_data()
            self.ui.addWidgetsToList(dlist)
            self.ui.edit.setText(app_name)
            self.ui.show()
            self.ui.edit.setFocus()

    def showAction(self, request={}):
        dlist=self.get_windows_data()
        self.ui.addWidgetsToList(dlist)
        self.ui.show()
        self.ui.edit.setFocus()

    def confirmAction(self, request={}):
        if self.ui.isVisible():
            item=self.ui.list.currentItem()
            self.set_window(item.itemData['id'])
            self.ui.edit.clear()
            self.ui.hide()
            self.checkAction(request)

    def set_window(self, wid):
        tree=asyncio.run(self.manager.get_tree())
        w=tree.find_by_id(wid)
        asyncio.run(w.command('focus'))

    def get_windows(self):
        tree=asyncio.run(self.manager.get_tree())
        windows={}
        for w in tree:
            if w.name in ['', None]: continue
            windows[w]=w.name
        return windows 

    def get_windows_data(self):
        windows=self.get_windows()
        items=[]
        for i3_window, name in windows.items():
            if i3_window.type!='con': continue
            if i3_window.name in ['content']+[str(i) for i in range(0, 11)]: continue
            if 'i3bar' in i3_window.name: continue
            workspace=i3_window.workspace().name
            items+=[{'top':name, 'down':f'Workspace {workspace}', 'id':i3_window.id}]
        return items

if __name__=='__main__':
    app=ApplicationsMode(port=33333)
    app.run()

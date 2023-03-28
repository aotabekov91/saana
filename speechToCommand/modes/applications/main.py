import os
import sys
import asyncio
import subprocess
import threading

from i3ipc.aio import Connection

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import GenericMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class ApplicationsMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(ApplicationsMode, self).__init__(
                 keyword='applications', 
                 info='Applications', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.ui=ListMainWindow(self, 'AppsMode - own_floating', 'Apps: ')
        self.commands={}
        self.set_commands()

    def showCommandsAction(self, request):
        self.ui.addWidgetsToList(self.commands)
        self.ui.edit.setFocus()
        self.ui.show()

    def showAction(self, request={}):
        dlist=self.get_windows()
        self.ui.addWidgetsToList(dlist)
        self.ui.edit.setFocus()
        self.ui.show()

    def openAction(self, request):
        slot_names=request['slot_names']
        app=slot_names.get('app', None)
        if app=='ranger':
            os.popen('kitty ranger')
        elif app=='mpv':
            os.popen('mpv ~/sciebo/music')
        else:
            os.popen(app)

    def confirmAction(self, request={}):
        if not self.ui.isVisible(): return
        item=self.ui.list.currentItem()
        if item.itemData['kind']=='command':
            subprocess.Popen(item.itemData['id'])
        else:
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
        items=[]
        for i3_window in tree:
            if i3_window.name in ['', None]: continue
            if i3_window.type!='con': continue
            if i3_window.name in ['content']+[str(i) for i in range(0, 11)]: continue
            if 'i3bar' in i3_window.name: continue
            workspace=i3_window.workspace().name
            items+=[{'top':i3_window.name,
                     'down':f'Workspace {workspace}',
                     'id':i3_window.id,
                     'kind':'application'}]
        return items

    def set_commands(self):
        def _set_commands():
            proc=subprocess.Popen(['pacman', '-Qe'], 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL
                                  )
            commandlications=proc.stdout.readlines()
            commands=[]
            for command in commandlications:
                info={}
                command=command.decode().strip('\n').split(' ')
                command_name=command[0]
                command_version=' '.join(command[1:])
                info['top']=command_name
                info['id']=command_name
                info['kind']='command'
                try:
                    proc=subprocess.Popen(['whatis', '-l',  command_name], 
                                          stderr=subprocess.DEVNULL,
                                          stdout=subprocess.PIPE)
                    desc=proc.stdout.readline().decode()
                    desc=desc.split('-', 1)[-1].strip()
                    info['down']=desc
                except:
                    info['down']=''
                commands+=[info]
            self.commands=commands

        t=threading.Thread(target=_set_commands)
        t.deamon=True
        t.start()

if __name__=='__main__':
    app=ApplicationsMode(port=33333)
    app.run()

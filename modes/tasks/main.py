import os
import sys
import zmq
import time
import json
import random

import playsound
from plyer import notification
from threading import Thread

from speechToCommand.modes.tasks.database import Database

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class Timer(QObject):

    finished=pyqtSignal()
    change=pyqtSignal()

    def __init__(self, parent):
        super(Timer, self).__init__()
        self.parent=parent
        self.duration=0
        self.active=True
        self.running=False

    def loop(self):
        while self.active:
            if not self.running:
                time.sleep(1)
            else:
                self.run_timer()

    def run_timer(self):
        while self.running and self.duration>0:
            self.duration-=1
            print(self.duration)
            self.change.emit()
            time.sleep(1)
        self.running=False
        self.finished.emit()

class TasksMode(QBaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(TasksMode, self).__init__(
                 keyword='tasks', 
                 info='Tasks', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.ui=ListMainWindow(self, 'Tasks - own_floating', 'Task: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)

        self.mode=None
        self.note=''
        self.work=60*self.config.getint('Custom', 'work')
        self.rest=60*self.config.getint('Custom', 'rest')

        self.db=Database(self.db_path, self.config)
        self.db.load_tasks()
        self.set_timer()

    def set_config(self):
        super().set_config()
        main_path=self.get_folder()
        quotes_path=f'{main_path}/{self.config.get("Custom", "quotes_path")}'
        self.quotes= json.load(open(quotes_path))
        self.sound_path=f'{main_path}/{self.config.get("Custom", "sound_path")}'
        self.db_path=f'{main_path}/{self.config.get("Custom", "database_path")}'

    def set_timer(self):
        self.timer_thread=QThread()
        self.timer=Timer(self)
        self.timer.moveToThread(self.timer_thread)
        self.timer.finished.connect(self.finishTask)
        self.timer.change.connect(self.reportStatus)
        self.timer_thread.started.connect(self.timer.loop)
        QTimer.singleShot(0, self.timer_thread.start)

    def showAction(self, request={}):
        self.tlist=self.getTasks()
        self.ui.addWidgetsToList(self.tlist)
        self.ui.show()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        self.setTask({'task_id': item.itemData['id'], 'task_name':item.itemData['top']})
        self.ui.hide()
        self.ui.edit.clear()

    def reportStatus(self):
        data={'countdown':self.timer.duration,
              'mode':self.mode,
              'task_id':self.task_id,
              'task_name':self.task_name,
              }

        query= {'command': 'storeData',
               'mode_name':self.__class__.__name__,
               'data_name':'status',
               'data':data}

        self.parent_socket.send_json(query)
        respond=self.parent_socket.recv_json()
        print(respond)

    def getTasks(self, request={}):
        tsks={}
        for i, j in self.db.task_chain.items():
            if i is None: continue
            tmp=[]
            for t in j:
                tmp+=[self.db.tasks[t[0]].desc]
            tsks['>'.join(tmp)]=i
        data=[{'top':n, 'id':t} for n, t in tsks.items()]
        return data

    def alertAction(self, kind=''):
        quote=self.quotes[random.randint(0, len(self.quotes))]
        def play():
            playsound.playsound(self.sound_path)

        t=Thread(target=play)
        t.start()

        notification.notify(
            title=f'{quote["text"]}\n\n{quote["author"]}\n',
            message='Time to {}{}'.format('have a rest'*(kind=='rest'), 'work'*(kind=='work')),
            timeout=120,
        )

    def finishTask(self, request={}):

        if self.mode=='work':
            worked_seconds=self.duration-self.timer.duration
            self.db.add_pomodoro_now(self.task_id, worked_seconds, self.note)
            self.alertAction('rest')
            self.mode='rest'
            self.timer.duration=self.rest
            self.timer.running=True
        elif self.mode=='rest':
            self.mode=None
            self.note=''
            self.duration=0
            self.task_name=''
            self.task_id=None
            self.timer.running=False
            self.alertAction('work')

    def setTask(self, request):
        self.task_id=request['task_id']
        self.note=request.get('rest', self.note)
        self.task_name=request.get('task_name', '')
        work=request.get('work', self.work)
        self.mode='work'
        self.duration=work
        self.timer.duration=work
        self.timer.running=True

    def exit(self, request={}):
        self.timer.active=False
        super().exit(request)

if __name__=='__main__':
    app=TasksMode(port=8234)
    app.run()
    sys.exit(app.exec_())

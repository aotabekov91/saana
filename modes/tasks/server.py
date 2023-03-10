#!/usr/bin/python3

import zmq
from cumodoro.database import Database
from cumodoro.config import TIME_POMODORO_SEC

db=Database()
db.load_tasks()

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5549")
socket.RCVTIMEO=1000

def get_tasks():
    tsks={}
    reverse={}
    for i, j in db.task_chain.items():
        if i is None: continue
        tmp=[]
        for t in j:
            tmp+=[db.tasks[t[0]].desc]
        tsks['>'.join(tmp)]=i
        reverse[i]='>'.join(tmp)
    return tsks, reverse

def get_status():
    socket.send_json({'request':'status'})
    r=socket.recv_json()
    return r

def finish_task():
    socket.send_json({'request':'finish_task'})
    r=socket.recv_json()
    return r

def add_task(self, task_name, color=None):
    pass

def set_task(task_id, duration=TIME_POMODORO_SEC, note=''):
    finish_task()
    socket.send_json({'request':'new_task', 'task_id':task_id, 'duration':duration, 'note':note})
    r=socket.recv_json()
    return r

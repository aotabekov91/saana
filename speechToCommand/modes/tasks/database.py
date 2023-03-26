import os
import sys
import logging
import datetime

import sqlite3 as sql
from collections import deque

class Task():
    pass

class Database():
    def __init__(self, db_path, config):
        self.db_path=db_path
        self.config=config
        self.db = None
        self.cursor = None
        self.tasks = None
        self.full_task_list = {}
        self.task_list = {}
        self.task_chain = {None:[]}
        self.has_savepoint = False

    def connect(self):
        if self.db == None:
            try:
                self.db = sql.connect(self.db_path, detect_types=sql.PARSE_DECLTYPES|sql.PARSE_COLNAMES, check_same_thread=False)
                self.db.isolation_level = None
                self.cursor = self.db.cursor()
                self.has_savepoint = False
            except sql.Error as e:
                print("Error:",e)
                sys.exit(1)

    def disconnect(self):
        if self.db != None:
            try:
                self.db.close()
                self.db = None
                self.cursor = None
            except sql.Error as e:
                print("Error:",e)
                sys.exit(1)

    def commit(self):
        try:
            if self.has_savepoint:
                raise Exception("Savepoint not released")
            self.db.commit()
        except sql.Error as e:
            print("Error:",e)
            sys.exit(1)

    def execute(self,query,params = None,immediate=True):
        if self.db == None:
            self.connect()

        if isinstance(query,str) and ( params == None or isinstance(params,tuple) ):
            if isinstance(params,tuple):
                self.cursor.execute(query,params)
            else:
                self.cursor.execute(query)

            if immediate:
                self.commit()
        else:
            raise Exception("parameter missmatch: string != "+str(type(query)))

    def request(self,query,params = None):
        if self.db == None:
            self.connect()

        self.execute(query,params)
        result = self.cursor.fetchall()
        return result

    def create(self):
        self.connect()

        try:

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    desc TEXT NOT NULL,
                    color INTEGER DEFAULT 0,
                    active INTEGER DEFAULT 1,
                    task INTEGER,
                    note TEXT
                )""")

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pomodoros (
                    id INTEGER PRIMARY KEY,
                    time TIMESTAMP NOT NULL,
                    duration INTEGER NOT NULL,
                    task INTEGER
                )""")

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    variable TEXT PRIMARY KEY NOT NULL,
                    value TEXT
                )""")

            try:
                self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_SLOT',str(config.TIME_SLOT)))
                self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_SLOT_NAME',str(config.TIME_SLOT_NAME)))
                self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_POMODORO',str(config.TIME_POMODORO)))
                self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_BREAK',str(config.TIME_BREAK)))
            except: pass

            self.db.commit()
        except sql.Error as e:
            print("Query Error on creation:",e)
            sys.exit(1)

    def update_config(self,variable,value):
        self.execute("UPDATE config SET value = ? WHERE variable == ?",(str(value),variable))

    def savepoint(self):
        if not self.has_savepoint:
            self.cursor.execute("savepoint cumodoro")
            self.has_savepoint = True
        else:
            raise Exception("Savepoint already present")

    def rollback(self):
        if self.has_savepoint:
            self.cursor.execute("rollback to savepoint cumodoro")
        else:
            raise Exception("Cannot rollback: savepoint doesn't exist")

    def release(self):
        if self.has_savepoint:
            self.cursor.execute("release savepoint cumodoro")
            self.has_savepoint = False
        else:
            raise Exception("Cannot release: savepoint doesn't exist")

    def load_tasks(self):
        if self.tasks != None:
            del self.tasks
            del self.colors

        self.full_task_list = {}
        self.task_list = {}
        self.tasks = {}
        t = Task()
        t.idx = None
        t.task = None
        t.color = 0
        t.active = 1
        t.desc = "None"
        self.tasks[t.idx] = t

        raw_tasks = self.request("SELECT id,task,color,active,desc FROM tasks")
        for entry in raw_tasks:
            idx, task, color, active, desc = entry
            t = Task()
            t.idx = idx
            t.task = task
            t.color = color
            t.active = active
            t.desc = desc
            self.tasks[idx] = t

            if idx not in self.task_list:
                self.task_list[idx] = []
            if task not in self.task_list:
                self.task_list[task] = []

            self.task_list[task].append(idx)

        self.full_task_list = dict(self.task_list)
        self.colors = {None:[0]}
        self.levels = 0
        if None in self.task_list:
            q = deque([[1,None,x] for x in self.task_list[None]])
            while q:
                level,parent,idx = q.popleft()
                if self.tasks[idx].active > 0:
                    q.extend([[level+1,idx,x] for x in self.task_list[idx]])

                    if idx not in self.colors:
                        self.colors.update({idx:[]})
                    color_list = []
                    if parent in self.colors:
                        color_list.extend(self.colors[parent])
                    self.colors[idx].extend(color_list)
                    self.colors[idx].append(self.tasks[idx].color)

                    if self.levels <= level:
                        self.levels = level + 1

                else:
                    q2 = deque([[idx,x] for x in self.task_list[idx]])
                    del self.task_list[parent][self.task_list[parent].index(idx)]
                    while q2:
                        level2,parent2,idx2 = q2.popleft()
                        q2.extend([[level2+1,idx2,x] for x in self.task_list[idx2]])
                        del self.task_list[idx2]

            for idx,color_list in self.colors.items():
                length = len(color_list)
                if length < self.levels:
                    if length > 0:
                        self.colors[idx].extend([color_list[-1] for i in range(self.levels - length)])
                    else:
                        self.colors[idx].extend([0 for i in range(self.levels - length)])

        self.task_chain = {None:[]}
        for task in self.tasks.keys():
            self.task_chain.update({task:self.find_task(task)})

    def find_task_rec(self,idx,l):
        for i in range(0,len(l)):
            if l[i] == idx:
                return [(l[i],i)]

            if l[i] in self.task_list:
                rl = self.find_task_rec(idx,self.task_list[l[i]])
                if len(rl) > 0:
                    rl.insert(0,(l[i],i))
                    return rl

        return []

    def find_task(self,idx):
        if None not in self.task_list:
            return []
        else:
            rl = self.find_task_rec(idx,self.task_list[None])
            return rl

    def get_todays_pomodoros(self):
        today=datetime.datetime.today()
        today=today.strftime('%Y-%m-%d')
        sql_query=f'select * from pomodoros where time like "%{today}%"'
        if self.db == None: self.connect()
        cursor = self.db.cursor()
        cursor.execute(sql_query)
        data=cursor.fetchall()
        plist=[]
        if len(data)>0:
            for d in data:
                plist+=[{'duration':d[-3],
                         'task':d[-2],
                         'note':d[-1]}]
        p_number=0
        p_time=0
        if len(plist)>0:
            for p in plist:
                p_number+=1
                if p['duration']=='': continue
                p_time+=p['duration']
        return p_number, p_time, plist

    def delete_task_rec(self,tl):
        for i in range(len(tl)):
            t = tl[i]
            self.delete_task_rec(self.task_list[t])
            log.debug("delete task "+str(t)+": "+str(self.task_list[t]))
            self.cursor.execute("DELETE FROM tasks WHERE id = ?",(t,))
            self.cursor.execute("UPDATE pomodoros SET task = ? WHERE task = ?",(None,t))

    def delete_task(self,idx,immediate = False):
        self.connect()
        self.delete_task_rec([idx])
        if immediate:
            self.db.commit()

    def store_task(self,e):
        if e.idx == None:
            data = (e.desc, e.color, e.active, e.task)
            self.execute("INSERT INTO tasks (desc,color,active,task) VALUES (?,?,?,?)",data)
            e.idx = self.cursor.lastrowid
        else:
            data = (e.desc, e.color, e.active, e.task, e.idx)
            self.execute("UPDATE tasks SET desc = ?, color = ?, active = ?, task = ? WHERE id = ?", data)

    def alter_pomodoro_task(self,idx,task,time=None,immediate=False):
        if idx == None:
            self.execute("INSERT INTO pomodoros (time,duration,task) VALUES (?,?,?)",
                         (time,self.config.get('Custom', 'work'),task), immediate)
        else:
            self.execute("UPDATE pomodoros SET task = ? WHERE id == ?",(task,idx),immediate)

    def delete_pomodoro(self,idx,immediate=False):
        if idx != None:
            self.execute("DELETE FROM pomodoros WHERE id = ?", (idx,), immediate)

    def add_pomodoro_now(self,task, actual_time_in_seconds=None, note=''):
        if actual_time_in_seconds is None:
            actual_time_in_seconds=self.config.get('Custom', 'work')
        if task == None:
            self.execute("INSERT INTO pomodoros (time,duration) VALUES (?,?,?)",(datetime.datetime.now(),actual_time_in_seconds,note))
        else:
            data = (datetime.datetime.now(),actual_time_in_seconds,task,note)
            self.execute("INSERT INTO pomodoros (time,duration,task,note) VALUES (?,?,?,?)",data)

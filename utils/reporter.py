import zmq
import json
import threading

class Reporter:
    def __init__(self, parent):
        self.parent=parent
        self.config=parent.config[self.__class__.__name__]
        self.port=int(self.config['port'])
        self.createConnection()

    def createConnection(self):
        self.rcontext=zmq.Context()
        self.rsocket=self.rcontext.socket(zmq.REP)
        self.rsocket.bind(f'tcp://*:{self.port}')

        reporterThread=threading.Thread(target=self.reporter)
        reporterThread.setDaemon(True)
        reporterThread.start()

    def reporter(self):

        def report(message):
            
            if message['command']=='currentMode':
                self.rsocket.send_json({'status':'ok', 'currentMode':self.parent.currentMode})
            elif message['command']=='previousMode':
                self.rsocket.send_json({'status':'ok', 'previousMode':self.parent.previousMode})
            elif message['command']=='setCurrentMode':

                mode_name=message.get('mode_name', False)
                mode_keyword=message.get('mode_keyword', False)
                if mode_name:
                    self.parent.setCurrentMode(mode_name)
                else:
                    mode_name=self.parent.keyword_to_mode_names.get(mode_keyword, False)
                    if mode_name: self.parent.setCurrentMode(mode_name)
                self.rsocket.send_json({'status':'ok', 'currentMode':self.parent.currentMode})

            elif message['command']=='setModeAction':
                mode_name=message['mode_name']
                mode_action=message['mode_action']
                intent_data=message['intent_data']
                self.parent.act(mode_name, mode_action, intent_data)
                self.rsocket.send_json({'status':'ok'}) 
            elif message['command']=='registerModeKeyword':
                self.parent.keyword_to_mode_names[message['keyword']]=message['mode_name']
                self.rsocket.send_json({'status':'ok'})
            else:
                self.rsocket.send_json({'status':'nok'})

        while True:
            message=self.rsocket.recv_json()
            report(message)

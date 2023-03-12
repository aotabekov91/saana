import sys
import subprocess

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class CommandMode(QBaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(CommandMode, self).__init__(
                 keyword='command', 
                 info='Command', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.commands=self.get_commands()
        self.ui=ListMainWindow(self, 'CommandMode - own_floating', 'Command: ')
        self.ui.addWidgetsToList(self.commands)

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        subprocess.Popen(item.itemData['id'])
        self.ui.edit.clear()
        self.ui.hide()

        self.parent_socket.send_json({'command':'setModeAction',
                                      'mode_name':'CheckerMode',
                                      'mode_action':'checkAction',
                                      })
        respond=self.parent_socket.recv_json()
        print(respond)

    def get_commands(self):
        proc=subprocess.Popen(['pacman', '-Qe'], stdout=subprocess.PIPE)
        commandlications=proc.stdout.readlines()
        commands=[]
        for command in commandlications:
            info={}
            command=command.decode().strip('\n').split(' ')
            command_name=command[0]
            command_version=' '.join(command[1:])
            info['top']=command_name
            info['id']=command_name
            try:
                proc=subprocess.Popen(['whatis', command_name], stdout=subprocess.PIPE)
                desc=proc.stdout.readline().decode()
                desc=desc.split('-', 1)[-1].strip()
                info['down']=desc
            except:
                info['down']=''
            commands+=[info]
        return commands

if __name__=='__main__':
    command=CommandMode(port=33333)
    command.run()

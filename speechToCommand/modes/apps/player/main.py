import os
import sys

import subprocess

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from speechToCommand.utils.moder import GenericMode
from speechToCommand.utils.helper import command
from speechToCommand.utils.widgets import ListMainWindow

class PlayerMode(GenericMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(PlayerMode, self).__init__(
                 keyword='player', 
                 info='Player controller', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes='all')

        self.current_player=''
        self.ui=ListMainWindow(self, 'PlayerMode - own_floating', 'Player: ')

    def get_player_list(self):

        proc=subprocess.Popen(['playerctl', '-l'], stdout=subprocess.PIPE)
        players=[p.decode().strip('\n') for p in proc.stdout.readlines()]

        data=[]
        proc=subprocess.Popen(
                ['playerctl', '-a', 'metadata', '--format',
                 '{{playerName}}__::::__{{artist}}__::::__{{title}}'],
                stdout=subprocess.PIPE)
        for i, p in enumerate(proc.stdout.readlines()):
            p=p.decode().strip('\n').split('__::::__')
            data+=[{'top':p[-1],
                    'down':'{}{}'.format(p[0], f' - {p[-2]}'*bool(p[-2])),
                    'id':players[i],
                    }]
        return data

    def showAction(self, request={}):
        self.ui.addWidgetsToList(self.get_player_list())
        self.ui.show()
        self.ui.edit.setFocus()

    def confirmAction(self, request={}):
        if self.ui.isVisible():
            item=self.ui.list.currentItem()
            self.current_player=item.itemData['id']
            self.ui.edit.clear()
            self.ui.hide()
    
    def get_current_player(self):
        if self.current_player:
            return f' -p {self.current_player} '
        return ' '

    @command()
    def playAction(self, request):
        return f'playerctl {self.get_current_player()} play'

    @command()
    def pauseAction(self, request):
        return f'playerctl {self.get_current_player()} pause'

    @command()
    def nextAction(self, request):
        return f'playerctl {self.get_current_player()} next'

    @command()
    def previousAction(self, request):
        return f'playerctl {self.get_current_player()} previous'

    @command()
    def increaseVolumeAction(self, request):
        return 'pactl set-sink-volume 0 +5%'

    @command()
    def decreaseVolumeAction(self, request):
        return 'pactl set-sink-volume 0 -5%'

    @command()
    def muteAction(self, request):
        return f'pactl set-sink-mute 0 toggle' 

if __name__=='__main__':
    app=PlayerMode(port=33333)
    app.run()

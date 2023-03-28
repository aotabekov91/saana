import asyncio
import subprocess

import libtmux
from i3ipc.aio import Connection

from .input import InputMode
from ..helper import command

class GenericMode(InputMode):

    def __init__(self, 
                 keyword='generic', 
                 info='Generic mode', 
                 port=None, 
                 parent_port=None, 
                 config=None,
                 window_classes='all',
                 app_name='own_floating'):

        super(GenericMode, self).__init__(
                 keyword=keyword, 
                 info=info, 
                 port=port, 
                 parent_port=parent_port, 
                 config=config,
                 window_classes=window_classes,
                 app_name=app_name
                )

        self.manager=asyncio.run(Connection().connect())
        self.tmux_server=libtmux.Server()

    def change_mode(self, mode_name=None):
        if mode_name=='me':
            mode_name=self.__class__.__name__
        if mode_name:
            self.parent_socket.send_json({'command':'setCurrentMode', 'mode_name':mode_name})
            respond=self.parent_socket.recv_json()

    def save_to_clipboard(self, request={}):
        slot_names=request['slot_names']
        text=slot_names.get('text', None)
        if text:
            self.clipboard().setText(text)

    def get_current_window(self):
        tree=asyncio.run(self.manager.get_tree())
        return tree.find_focused()

    def get_window_class(self):
        window=self.get_current_window()
        if window.name=='tmux':
            cmd=('list-panes', '-F', '#{pane_id}:#{pane_pid}:#{pane_active}')
            r=self.tmux_server.cmd(*cmd)
            for pane_data in r.stdout:
                pane_id, pid, active=tuple(pane_data.split(':'))
                if active=='1':
                    cmd=f'ps -o cmd --no-headers --ppid {pid}'.split(' ')
                    w=subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    processes=w.stdout.readlines()
                    if len(processes)>0:
                        process_name=(processes[-1]
                                      .decode()
                                      .strip('\n')
                                      .lower()
                                      )
                        for f in ['vim', 'ranger']:
                            if f in process_name: return f
            return 'tmux'
        else:
            return window.window_class

    def parse_repeats(self, request):
        slot_names=request.get('slot_names', {})
        return int(slot_names.get('repeat', 1.))

    def editorAction(self, slot_names): 
        if self.parent_port:
            slot_names['client']=self.__class__.__name__
            self.parent_socket.send_json({
                    'command': 'setModeAction',
                    'mode_name' : 'EditorMode',
                    'mode_action': 'activateAction',
                    'slot_names':slot_names,
                    })
            print(self.parent_socket.recv_json())

    def checkAction(self, request={}):
        window_class=self.get_window_class()
        if self.parent_port:
            self.parent_socket.send_json(
                    {'command':'setCurrentWindow',
                     'request': request, 
                     'window_class': window_class,
                     })
            return self.parent_socket.recv_json()

    def lockAction(self, request):
        self.parent_socket.send_json({
            'command': 'lockAction',
            'mode_name':self.__class__.__name__,
            'mode_action': 'lockListenAction',})
        respond=self.parent_socket.recv_json()

    @command(checkActionOnFinish=True)
    def unlockAction(self, request):
        self.parent_socket.send_json({
            'command': 'unlockAction',
            'mode_name':self.__class__.__name__})
        respond=self.parent_socket.recv_json()

    @command(checkActionOnFinish=True)
    def lockListenAction(self, request):
        text=request['slot_names']['text']
        slots=request['slot_names']['slots']
        action=request['slot_names']['command']
        if action:
            command=action.split('_')[-1]
            action=getattr(self, command, None)
            if not action and hasattr(self, 'ui'):
                action=getattr(self.ui, command, None)
        if action and 'magic' in text:
            action({'slot_names':slots})
        else:
            text=text.replace(' ', '" "').strip()
            return f'xdotool getactivewindow type {text}" "'

    @command(checkActionOnFinish=True, checkWindowType=False)
    def confirmAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Enter'

    @command(checkWindowType=False)
    def cancelAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} Escape'

    @command(checkWindowType=False)
    def forwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+f'

    @command(checkWindowType=False)
    def backwardAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} ctrl+b'

    @command(checkWindowType=False)
    def nextAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} space'

    @command(checkWindowType=False)
    def previousAction(self, request):
        return 'xdotool getactivewindow key --repeat {repeat} shift+space'

    @command(checkWindowType=False, windowCommand=True)
    def fullscreenAction(self, request):
        return 'fullscreen toggle'
    
    @command(checkWindowType=False)
    def zoomInAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} plus'

    @command(checkWindowType=False)
    def zoomOutAction(self, request={}):
        return 'xdotool getactivewindow key --repeat {repeat} minus'

    @command(checkActionOnFinish=False)
    def changeModeAction(self, request):
        slot_names=request['slot_names']
        mode_name=slot_names.get('mode', None)
        if mode_name: self.change_mode(mode_name)

    @command(checkActionOnFinish=True)
    def escapeAction(self, request):
        super().escapeAction(request)
        self.unlockAction(request)

if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

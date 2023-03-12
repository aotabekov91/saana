import os
import sys
import subprocess

from speechToCommand.utils.moder import BaseMode

class FehMode(BaseMode):
    def __init__(self, port=None, parent_port=None, config=None):
        super(FehMode, self).__init__(
                 keyword='feh', 
                 info='feh', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

    def check_window_class(self):
        self.generic.set_current_window()
        if self.generic.current_window.window_class=='feh':
            return True
        else:
            if self.parent_port:
                self.parent_socket.send_json({'command':'setModeAction',
                                              'mode_name':'CheckerMode',
                                              'mode_action':'checkAction',
                                              })
                respond=self.parent_socket.recv_json()
                print(respond)
            return False

    def forwardAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key j')

    def backwardAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key k')

    def zoomInAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type s')

    def zoomOutAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type a')

    def moveUpAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+j')

    def moveDownAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+k')

    def moveRightAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+l')

    def moveLeftAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key shift+h')


if __name__=='__main__':
    app=FehMode(port=33333)
    app.run()

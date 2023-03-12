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
            return False

    def activateAction(self, request):
        if self.check_window_class():
            self.generic.set_current_window()
            self.current_window=self.generic.current_window

    def spaceAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key j')

    def spaceShiftAction(self, request):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow key k')

    def zoomInAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type s')

    def zoomOutAction(self, request={}):
        if self.check_window_class():
            os.popen(f'xdotool getactivewindow type a')

if __name__=='__main__':
    app=FehMode(port=33333)
    app.run()

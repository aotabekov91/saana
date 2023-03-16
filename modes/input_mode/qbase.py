import sys
import zmq
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Inputer(QApplication):

    def __init__(self):

        super(Inputer, self).__init__()

        self.setApplicationName('Inputer - own_floating')

    def run(self):
        sys.exit(self.exec_())

    def exit(self, request={}):
        self.close()

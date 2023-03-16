import os
import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from .generic_mode import BaseGenericMode 
from speechToCommand.utils.widgets.qapplication import QBaseApplication 

class QBaseGenericMode(BaseGenericMode, QBaseApplication):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 window_classes=[],
                 argv=[],
                 ):
                 
        super(QBaseGenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                argv=argv,
                )

    def run(self):
        sys.exit(self.exec_())

    def exit(self, request={}):
        self.zeromq_listener.wait=False
        self.zeromq_listener.running=False
        if self.ui: self.ui.close()
        self.close()


if __name__=='__main__':
    app=QBaseGenericMode(port=33333, parent_port=44444)
    app.run()

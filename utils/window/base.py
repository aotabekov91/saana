import os
import sys
import zmq
import time
import subprocess

import asyncio

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.helper import osGenericCommand

class BaseGenericMode(BaseMode):
    def __init__(self,
                 keyword='generic',
                 info='Generic window commands',
                 port=None,
                 parent_port=None,
                 config=None, 
                 window_classes=[],
                 argv=None):

        super(BaseGenericMode, self).__init__(
                keyword=keyword,
                info=info,
                port=port,
                parent_port=parent_port,
                config=config,
                window_classes=window_classes,
                argv=argv,
                )
        
if __name__=='__main__':
    app=GenericMode(port=33333, parent_port=44444)
    app.run()

from .speechToCommand import utils
from .speechToCommand import SpeechToCommand 
from .speechToCommand import SpeechToCommandCLI 

from tendo import singleton

def run():
    try:

        me=singleton.SingleInstance()

        app=SpeechToCommand()
        app.run()

    except singleton.SingleInstanceException:

        print('An instance of SpeechToCommand is already running!')

if __name__=='__main__':
    run()

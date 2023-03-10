from .main import *

from tendo import singleton

def run():
    try:

        me=singleton.SingleInstance()

        parser=argparse.ArgumentParser()
        parser.add_argument('--listener', nargs='?', type=bool, default=False)
        args=parser.parse_args()
        r=SpeechToCommand()
        if args.listener: r.set_listener()
        r.run()

    except singleton.SingleInstanceException:

        print('An instance of SpeechToCommand is already running!')

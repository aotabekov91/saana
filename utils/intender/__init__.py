from multiprocessing import Process

from .intender import Intender

def get_intender(port):

    def run(port):
        app=Intender(port)
        app.run()

    p=Process(target=run, args=(port,))
    p.start()
    return p

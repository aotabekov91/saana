import os
import sys

from plug.plugs.handler import Handler

class Saana(Handler):

    def setup(self):
        raise

def run():

    app=Saana()
    app.run()

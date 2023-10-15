from plug import Plug
from saana.generic import Generic
from plug.plugs.moder import Moder
from plug.plugs.picky import Picky
from plug.plugs.umay_plug import Umay

class Saana(Plug):

    def loadModer(self):

        self.moder.load(
                plugs=set([Picky, Generic]),
                    )
        self.moder.load(
                plugs=set([Umay])
                )

    def setup(self):

        super().setup()
        self.setModer(
                Moder,
                default='Generic'
                )
        self.loadModer()

def run():
    Saana()

from saana.generic import Generic
from plug.plugs.umay_plug import Umay
from plug.plugs.handler import Handler

class Saana(Handler):

    def loadModer(self):

        prms={'pollerize': False}
        super().loadModer(
                plugs=set([Generic, Umay]),
                plug_prmts={'Umay': prms},
                )

    def setup(self):

        super().setup()
        self.setModer()
        self.setConnect(
                kind='REP',
                socket_kind='bind',
                )

    def handle(self, request):

        umay=self.moder.plugs.umay
        res=umay.send({'getState':{}})
        prev=res['getState'].get('prev')
        if prev and prev!=self.name:
            data= {'app':prev, 'action':request}
            res=umay.send({'act':data})
            print('Saana rerouting to {prev}:', res)

def run():

    app=Saana()
    app.run()

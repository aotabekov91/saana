from plug import Plug

class Generic(Plug):

    def setup(self):

        super().setup()
        self.functions={
                'setApp': self.setApp,
                'setMode': self.setMode,
                }

    def setMode(self, mode=None):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send({'getState':{}})
        prev_app=res['getState'].get('prev_app')

        if prev_app!=self.app.name:
            action={'Generic_setMode':{'mode':mode}}
            data = {
                'app':prev_app, 
                'action':action
               }
            res = self.umay.send(
                {'act':data})
            print(res)
        else:
            super().setMode(mode)
        data = {'mode':mode}
        res = self.umay.send(
            {'setMode':data})
        print(res)

    def setApp(self, app=None):

        self.umay=self.app.moder.plugs.umay
        if app:
            data={'setApp': {'app':app}}
            res=self.umay.send(data)
            print(res)

    def handleRequest(self, request):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send(
                {'getState':{}})
        prev=res['getState'].get('prev_app')
        if prev!=self.app.name:
            data = {
                    'app':prev, 
                    'action':request
                   }
            res = self.umay.send({'act':data})
            print(f'Saana rerouting to {prev}:', res)
        else:
            self.runPlugAction(request)


    def runPlugAction(self, request):

        for n, prm in request.items():
            np=self.umay.parseName(n)
            if np:
                mode, action = np 
                plug=self.app.moder.current
                if plug:
                    f=plug.functions.get(
                            action, None)
                    self.umay.adjustParameters(
                            prm)
                    if f: f(**prm)

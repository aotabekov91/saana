from plug import Plug

class Generic(Plug):

    def setup(self):

        super().setup()
        self.functions={
                'setApp': self.setApp,
                'setMode': self.setMode,
                'showState': self.showState,
                }

    def getApps(self, mode):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send({'getKeywords':{}})
        res=res.get('getKeywords', {})
        k=res.get('keywords', {})
        matches=[]
        for app, data in k.items():
            for m in data.get('mode', []):
                if mode in m:
                    matches+=[app]
        return matches

    def showState(self):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send({'getState':{}})
        print(res)

    def setMode(self, mode=None):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send({'getState':{}})
        prev=res['getState'].get('prev_app')
        if prev==self.app.name or not prev:
            super().setMode(mode)
        else:
            action={'Generic_setMode':{'mode':mode}}
            data = {
                'app':prev, 
                'action':action
               }
            res = self.umay.send(
                {'act':data})
            print(res)
        apps=self.getApps(mode)
        if len(apps)==1:
            self.setApp(apps[0])
        res = self.umay.send(
                {'setMode': {'mode':mode}}
             )
        print(res)

    def setApp(self, app=None):

        self.umay=self.app.moder.plugs.umay
        if app:
            data={'setApp': {'app':app}}
            res=self.umay.send(data)
            print(res)

    def handleRequest(self, request):

        self.umay=self.app.moder.plugs.umay
        res=self.umay.send({'getState':{}})
        prev=res['getState'].get('prev_app')
        if prev==self.app.name or not prev:
            self.runPlugAction(request)
        else:
            data = {
                    'app':prev, 
                    'action':request
                   }
            res = self.umay.send({'act':data})
            print(f'Saana rerouting to {prev}:', res)

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

from plug import Plug

class Generic(Plug):

    def check(self):
        raise

    def setApplication(self, app=None):

        if app:
            data={'setState': {'app':app}}
            umay=self.app.moder.plugs.get('umay')
            if umay:
                res=umay.send(data)
                print(res)

    def handle(self, request):
        self.app.handle(request)

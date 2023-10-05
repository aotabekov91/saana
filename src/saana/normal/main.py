from plug import Plug

class Normal(Plug):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.prev=None
        self.current=None

    def checkApp(self):
        raise

    def setApp(self, app):

        self.prev=self.current
        self.current=app

    def handle(self, request):

        msg=f'Rerouting {request} to: '
        print(msg, self.current)
        self.app.setAction(
                    self.current, request)

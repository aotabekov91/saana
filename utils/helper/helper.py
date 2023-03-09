import sys

def respond(func):
    def inner(self, request):
        try:
            func(self, request)
            msg='{name}: Success'.format(name=func.__name__)
        except:
            err_type, error, traceback = sys.exc_info()
            msg='{name}: {err}'.format(name=func.__name__, err=error)
        if request!=None and len(request)>0:
            self.socket.send_json({'status':msg})
            self.stop_waiting()
    return inner

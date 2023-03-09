import sys

class Window: 

    def handle_request(self, request):
        print(f'{self.__class__.__name__}: UI handling request')
        command=request['command'].split('_')[-1]
        action=getattr(self, command, False)
        if action: action(request)

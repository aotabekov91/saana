import sys
import asyncio
import subprocess
from i3ipc.aio import Connection

from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class ApplicationsMode(Mode):
    def __init__(self, config):
        super(ApplicationsMode, self).__init__(config, keyword='applications', info='Applications')
        self.ui=ListMainWindow('AppsMode - own_floating', 'Apps: ')

        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.ui.show_signal.connect(self.showAction)
        self.ui.choose_signal.connect(self.chooseAction)
        self.ui.confirm_signal.connect(self.confirmAction)
        self.ui.open_signal.connect(self.openAction)

        self.mode=None
        self.get_applications_data()

    def openAction(self, request={}):
        print('Applications to show')
        self.mode='open'
        self.ui.list.clear()
        self.ui.addWidgetsToList(self.apps)
        self.ui.show()

    def chooseAction(self, request={}):
        _, __, ___, slots=self.parse_request(request)
        app_name=''
        if slots: app_name=slots[0]['value']['value']

        if self.mode=='show':
            self.dlist=self.get_windows_data()
        elif self.mode=='open':
            self.dlist=self.apps
        self.ui.addWidgetsToList(self.dlist)
        self.ui.edit.setText(app_name)
        self.ui.show()

    def showAction(self, request={}):
        self.mode='show'
        self.dlist=self.get_windows_data()
        self.ui.addWidgetsToList(self.dlist)
        self.ui.show()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        self.set_window(item.itemData['id'])
        self.ui.edit.clear()
        self.ui.hide()

    async def get_windows(self):
        i3=await Connection().connect()
        tree=await i3.get_tree()
        windows={}
        for w in tree:
            if w.name in ['', None]: continue
            windows[w]=w.name
        return windows, tree

    def set_window(self, wid):
        if self.mode=='show':
            windows, tree=asyncio.run(self.get_windows())
            w=tree.find_by_id(wid)
            asyncio.run(w.command('focus'))
        elif self.mode=='open':
            subprocess.Popen(wid)

    def get_applications_data(self):
        proc=subprocess.Popen(['pacman', '-Qe'], stdout=subprocess.PIPE)
        applications=proc.stdout.readlines()
        self.apps=[]
        for app in applications:
            info={}
            app=app.decode().strip('\n').split(' ')
            app_name=app[0]
            app_version=' '.join(app[1:])
            info['top']=app_name
            info['id']=app_name
            self.apps+=[info]


    def get_windows_data(self):
        windows, _=asyncio.run(self.get_windows())
        items=[]
        for i3_window, name in windows.items():
            if i3_window.type!='con': continue
            if i3_window.name in ['content']+[str(i) for i in range(0, 11)]: continue
            if 'i3bar' in i3_window.name: continue
            workspace=i3_window.workspace().name
            items+=[{'top':name, 'down':f'Workspace {workspace}', 'id':i3_window.id}]
        return items

if __name__=='__main__':
    app=ApplicationsMode({'port':8234})
    app.dlist=app.get_windows_data()
    app.ui.addWidgetsToList(app.dlist)
    app.ui.show()
    sys.exit(app.exec_())

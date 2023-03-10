import sys

from cumodoro import server

from speechToCommand.utils.moder import BaseMode
from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class TasksMode(QBaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(TasksMode, self).__init__(
                 keyword='tasks', 
                 info='Tasks', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.ui=ListMainWindow(self, 'Tasks - own_floating', 'Task: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)

    def showAction(self, request):
        self.tlist=self.get_tasks()
        self.ui.addWidgetsToList(self.tlist)
        self.ui.show()

    def chooseAction(self, request):
        task_name=request['slot_names'].get('item', '')
        self.ui.edit.setText(task_name)
        self.ui.show()

    #todo server hangs here for server.set_task
    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        server.set_task(item.itemData['id'])
        self.ui.hide()
        self.ui.edit.clear()

    def get_tasks(self):
        tasks, reverse=server.get_tasks()
        data=[{'top':n, 'id':t} for n, t in tasks.items()]
        return data

if __name__=='__main__':
    app=TasksMode({'port':8234})
    app.tlist=app.get_tasks()
    app.ui.addWidgetsToList(app.tlist)
    app.ui.show()
    sys.exit(app.exec_())

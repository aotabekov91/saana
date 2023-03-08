import sys

from cumodoro import task
from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class TasksMode(Mode):

    def __init__(self, config):

        super(TasksMode, self).__init__(config, keyword='tasks', info='Tasks')
        self.ui=ListMainWindow('Tasks - own_floating', 'Task: ')
        self.ui.edit.returnPressed.connect(self.confirmAction)
        self.ui.show_signal.connect(self.showAction)
        self.ui.choose_signal.connect(self.chooseAction)

    def handleRequest(self, request):
        if request['command']=='TasksMode_finishTask':
            task.finish_task()
        else:
            super().handleRequest(request)
                
    def showAction(self, request):
        self.tlist=self.get_tasks()
        self.ui.addWidgetsToList(self.tlist)
        self.ui.show()

    def chooseAction(self, request):
        self.tlist=self.get_tasks()
        self.ui.addWidgetsToList(self.tlist)
        _, __, ___, slots=self.parse_request(request)
        task_name=''
        if slots: task_name=slots[0]['value']['value']
        self.ui.edit.setText(task_name)
        self.ui.show()

    def confirmAction(self, request={}):
        item=self.ui.list.currentItem()
        if item: task.set_task(item.itemData['id'])
        self.ui.hide()
        self.ui.edit.clear()

    def get_tasks(self):
        tasks, reverse=task.get_tasks()
        data=[{'top':n, 'id':t} for n, t in tasks.items()]
        return data

if __name__=='__main__':
    app=TasksMode({'port':8234})
    app.tlist=app.get_tasks()
    app.ui.addWidgetsToList(app.tlist)
    app.ui.show()
    sys.exit(app.exec_())

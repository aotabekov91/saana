import os
import sys
import json
import logging
import subprocess

from speechToCommand.utils.moder import Mode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class BookmarkMode(Mode):

    def __init__(self, config):
        super(BookmarkMode, self).__init__(config, keyword='bookmarks', info='Bookmarks')
        self.support_browsers = ['google-chrome', 'chromium']
        self.bookmarks_paths = self.find_bookmarks_paths()
        self.bookmarks=self.get_bookmarks()

        self.ui=ListMainWindow('Bookmarks - own_floating', 'Bookmark: ')
        self.ui.returnPressed.connect(self.confirmAction)
        self.ui.addWidgetsToList(self.bookmarks)

    def confirmAction(self, request={}):
        if not self.ui.isVisible(): return
        citem=self.ui.list.currentItem()
        subprocess.Popen(['xdg-open', citem.itemData['id']])

    def find_bookmarks_paths(self):
        res_lst = []
        for browser in self.support_browsers:
            f = os.popen('locate %s | grep Bookmarks' % browser)
            res = f.read().split('\n')
            for one_path in res:
                if one_path.endswith('Bookmarks'):
                    res_lst.append((one_path, browser))
            res_lst.append(
                    (os.path.expanduser('~/.config/google-chrome/Default/Bookmarks'), 'google-chrome'))
        return res_lst

    def find_rec(self, data, matches):
        if data['type'] == 'folder':
            for child in data['children']:
                self.find_rec(child, matches)
        else:
            matches.append(data)

    def get_bookmarks(self):
        bookmarks=[]
        for bookmarks_path, browser in self.bookmarks_paths:
            with open(bookmarks_path) as data_file:
                matches=[]
                data = json.load(data_file)
                self.find_rec(data['roots']['bookmark_bar'], matches)
            for bookmark in matches:
                bookmarks+=[{'top':bookmark['name'], 'id':bookmark['url']}]
        return bookmarks

if __name__=='__main__':
    app=BookmarkMode({'port':8234})
    app.showAction()
    sys.exit(app.exec_())

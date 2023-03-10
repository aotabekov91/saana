import os
import sys
import json
import logging
import subprocess

from speechToCommand.utils.moder import QBaseMode
from speechToCommand.utils.widgets.qlist import ListMainWindow

class BookmarkMode(QBaseMode):

    def __init__(self, port=None, parent_port=None, config=None):
        super(BookmarkMode, self).__init__(
                 keyword='bookmarks', 
                 info='Bookmarks', 
                 port=port, 
                 parent_port=parent_port, 
                 config=config)

        self.support_browsers = ['google-chrome', 'chromium']
        self.bookmarks_paths = self.find_bookmarks_paths()
        self.bookmarks=self.get_bookmarks()

        self.ui=ListMainWindow(self, 'Bookmarks - own_floating', 'Bookmark: ')
        self.ui.returnPressed.connect(self.confirmAction)
        self.ui.addWidgetsToList(self.bookmarks)

    def confirmAction(self, request={}):
        if not self.ui.isVisible(): return
        citem=self.ui.list.currentItem()
        subprocess.Popen(['xdg-open', citem.itemData['id']])
        self.ui.hide()


    def deleteAction(self, request={}):
        pass

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
            for i, bookmark in enumerate(matches):
                bookmarks+=[{'top':bookmark['name'], 'id':bookmark['url']}]
                if i>self.config.getint('Custom', 'max_number'): return bookmarks
        return bookmarks

if __name__=='__main__':
    app=BookmarkMode(port=33333)
    app.run()

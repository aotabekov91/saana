import os
import time
import inspect
from multiprocessing import Process
from configparser import ConfigParser

from speechToCommand import modes

class Loader:
    def __init__(self, config=None, include=[], exclude=[]):

        self.config=config
        self.port=None
        self.exclude=exclude
        self.include=include
        self.set_config()

    def set_config(self):
        if self.config is None:
            file_path=os.path.abspath(inspect.getfile(self.__class__))
            mode_path=os.path.dirname(file_path).replace('\\', '/')
            config_path=f'{mode_path}/config.ini'
            if os.path.isfile(config_path):
                self.config=ConfigParser()
                self.config.read(config_path)

            if self.config.has_section('General'):
                self.port=self.config.getint('General', 'handler_port')
                if self.config.has_option('Modes', 'exclude'):
                    if len(self.exclude)==0:
                        self.exclude=self.config.get('Modes', 'exclude')
                if self.config.has_option('Modes', 'include'):
                    if len(self.include)==0:
                        self.include=[
                                f.strip() for f in self.config.get(
                                    'Modes', 'include').split(' ')
                                      ]

    def run_in_background(self, mode_class, kwargs):
        def start(mode_class, kwargs):
            app=mode_class(**kwargs)
            app.run()
        t=Process(target=start, args=(mode_class, kwargs))
        t.start()

    def load_modes(self):

        for m in modes.__dir__():
            if m.startswith('__'): continue
            mode_package=getattr(modes, m)
            get_mode=getattr(mode_package, 'get_mode', False)
            
            if get_mode:
                mode_class=mode_package.get_mode()

                mode_name=mode_class.__name__
                if mode_class in self.exclude: continue
                if len(self.include)>0 and not mode_name in self.include: continue
                try:
                    self.run_in_background(mode_class, {'parent_port': self.port})
                    print('Loaded: ', mode_class) 
                    time.sleep(5)
                except:
                    print(f'Could not load: {mode_class.__name__}')

if __name__=='__main__':
    app=Loader()
    app.load_modes()

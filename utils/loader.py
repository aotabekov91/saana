import os
import sys
from multiprocessing import Process

from speechToCommand import modes
from speechToCommand.utils.porter import find_unused_port

class Loader:

    def __init__(self, config):
        self.config=config
        self.assigned_ports=[]

    def assign_port(self, config):
        if not hasattr(config, 'port'):
            port=find_unused_port(8001, self.assigned_ports)
            self.assigned_ports+=[port]
            config['port']=port

    def load_new_type_modes(self):
        pass


    def load_modes(self):
        loaded_modes={}
        modes_path=modes.__path__[0]
        for m in modes.__dir__():
            if m.startswith('__'): continue
            mode_package=getattr(modes, m)
            mode_class=mode_package.get_mode()
            mode_class.intents_yaml_paths=[f'{modes_path}/{m}/intents.yaml']
            mode_config=self.config.get(mode_class.__name__, {}, fallback={})
            mode_config['parent_port'] =self.config['Reporter']['port']
            self.assign_port(mode_config)

            try:
                self.run(mode_class, mode_config)
                loaded_modes[mode_class.__name__]=(mode_class, int(mode_config['port']))
            except:
                print(f'Could not load: {mode_class.__name__}')

        return loaded_modes

    def run(self, mode_class, mode_config):

        def start(mode_class, mode_config):
            app=mode_class(mode_config)
            sys.exit(app.exec_())

        t=Process(target=start, args=(mode_class, mode_config))
        t.start()

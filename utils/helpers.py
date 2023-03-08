import os
import sys
import socket

from pathlib import Path

from multiprocessing import Process
from configparser import ConfigParser

PORT_RANGE = list(range(8001, 12100))

def get_gconfig():
    utils_folder=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    main_path=Path(utils_folder).parent.absolute()
    p=ConfigParser()
    p.read(f'{main_path}/config.ini')
    return p

def run_mode(mode_class):
    def start(mode_class):
        app=mode_class()
        app.run()
    p=Process(target=start, args=(mode_class))
    p.start()
    return p

def load_modes():

    loaded_modes=[]
    utils_folder=os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    main_path=Path(utils_folder).parent.absolute()
    modes_path=f'{main_path}/modes'
    sys.path.append(modes_path)
    for mode_module in os.listdir(modes_path):
        if mode_module.startswith('__'): continue
        if not os.path.isfile(f'{mode_module}/__init__.py'): continue
        from mode_module import get_mode
        loaded_modes+=[run_mode(get_mode())]
    return loaded_modes

def find_port(default=8001, exclude_list=[]):
    """
    Returns first free port in range :data:`PORT_RANGE`

    :param int default:
    :rtype: int
    """
    to_select = [default] + PORT_RANGE
    for port in to_select:
        if not is_port_in_use(port) and not port in exclude_list:
            return port

    raise Exception("Could not find an unused port")

def is_port_in_use(port, host='127.0.0.1'):
    """
    :rtype bool:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    return result == 0

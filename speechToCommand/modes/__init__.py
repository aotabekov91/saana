from . import input_mode
from . import clipboard_mode
from . import change_mode
from . import generic_mode

from . import applications
from . import windows_manager
from . import keyboard
from . import notify
from . import tasks
from . import wiki
from . import command_mode

from .window_modes import anki
from .window_modes import player
from .window_modes import vim
from .window_modes import qutebrowser
from .window_modes import ranger
from .window_modes import tmux
from .window_modes import feh

try:
    from . import lookup
except:
    pass

try:
    from . import generator
except:
    pass

try:
    from . import open_ai #todo browser is not showing within a python environment
except:
    pass



# <---->

# from .window_modes import sioyek
# from . import translator
# from . import bookmarks

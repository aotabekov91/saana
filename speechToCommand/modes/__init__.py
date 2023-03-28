from . import windows 

from . import editor
from . import applications
from . import notify
from . import tasks
from . import wiki

from .apps import feh
from .apps import player
from .apps import vim

from .apps import qutebrowser
from .apps import chrome
from .apps import ranger
from .apps import tmux
from .apps import anki

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

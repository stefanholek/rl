"""Alternative Python bindings for GNU Readline."""

__all__ = ['completer', 'completion', 'history', 'readline',
           'generator', 'print_exc']

# Grab the PyOS_ReadlineFunctionPointer
from rl import _init
from rl import readline

# For subclassing and Sphinx
from rl._completion import Completer
from rl._completion import Completion
from rl._history import History

# API
from rl._completion import completer
from rl._completion import completion
from rl._completion import generator
from rl._completion import print_exc
from rl._history import history

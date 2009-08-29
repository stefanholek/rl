"""Alternative readline interface focusing on completion."""

from _stdlib import readline # [sic]
del readline

from _readline import *
from _completer import completer
from _completer import generator
from _completer import print_exc
from _completion import completion
from _history import history

# For subclassing
from _completer import Completer
from _completion import Completion
from _history import History

# Patch cmd.Cmd to use rl instead of readline
import _cmd

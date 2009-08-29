"""Alternative readline interface focusing on completion."""

from stdlib import readline # [sic]
from _readline import *

from _completer import completer
from _completer import generator
from _completer import print_exc
from _completion import completion
from _history import history

# Patch cmd.Cmd to use rl instead of readline
import _cmd

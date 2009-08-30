"""Alternative readline interface focusing on completion."""

from _stdlib import readline # [sic]
import _readline as readline

from _completer import completer
from _completion import completion
from _history import history
from _utils import generator
from _utils import print_exc

# For subclassing
from _completer import Completer
from _completion import Completion
from _history import History

# Patch cmd.Cmd to use rl instead of readline
import _cmd

"""Alternative readline interface focusing on completion.

completer
    Interface to the readline completer.

completion
    Interface to the active readline completion.

history
    Interface to the readline history.

readline
    Basic readline interface module.

generator
    Generator function factory.

print_exc
    Decorator printing exceptions to stderr.
"""

# Grab the ReadlineFunctionPointer
import readline
import _readline as readline

# Patch cmd.Cmd to use rl instead of readline
import _cmd

# For subclassing
from _completion import Completer
from _completion import Completion
from _history import History

# API
from _completion import completer
from _completion import completion
from _completion import generator
from _completion import print_exc
from _history import history

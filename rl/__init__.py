"""Alternative readline interface focusing on completion."""

# Grab the ReadlineFunctionPointer
import readline
import _readline as readline

# Patch cmd.Cmd to use rl instead of readline
import _cmd

# API
from _completion import completer
from _completion import completion
from _completion import generator
from _completion import print_exc
from _history import history

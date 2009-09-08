"""Alternative readline interface focusing on completion."""

# Make sure we can grab the ReadlineFunctionPointer
from stdlib import readline
import readline

# Patch cmd.Cmd to use rl instead of readline
import cmd

from completion import completer
from completion import completion
from completion import generator
from completion import print_exc

from history import history

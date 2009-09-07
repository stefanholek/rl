"""Alternative readline interface focusing on completion."""

# Make sure we can grab the ReadlineFunctionPointer
from stdlib import readline
import readline

# Patch cmd.Cmd to use rl instead of readline
import cmd

import completion
import history

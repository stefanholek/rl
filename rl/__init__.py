"""Alternative readline interface focusing on completion.

Example::

    from rl import completer
    from rl import completion
    from rl import generator

    strings = ['foo-', 'bar-', 'baz+']

    def complete(text):
        completion.suppress_append = True
        return [x for x in strings if x.startswith(text)]

    completer.completer = generator(complete)
    completer.parse_and_bind('tab: complete')
    line = raw_input('> ')
"""

# Make sure we can grab the ReadlineFunctionPointer
from stdlib import readline
import readline

# Patch cmd.Cmd to use rl instead of readline
import cmd

# This makes epydoc cry
from completion import completer
from completion import completion
from completion import generator
from completion import print_exc

from history import history

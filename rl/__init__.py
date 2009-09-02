"""Alternative readline interface focusing on completion."""

import readline # [sic]
import _readline as readline

from _completer import Completer
from _completion import Completion
from _history import History
from _utils import GeneratorFunction

# Interface objects
completer = Completer()
completion = Completion()
history = History()

# Patch cmd.Cmd to use rl instead of readline
import _cmd


def generator(compfunc):
    """Generator function factory.

    Takes a callable returning a list of matches and returns an
    object implementing the generator protocol readline expects.
    """
    return GeneratorFunction(compfunc)


def print_exc(func):
    """Decorator printing exceptions to stderr.

    Useful when debugging completions and hooks, as exceptions occurring
    there are usually swallowed by the in-between C code.
    """

    def wrapped_func(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            import traceback; traceback.print_exc()
            raise

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func


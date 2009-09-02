"""Alternative readline interface focusing on completion."""

import readline # [sic]
import _readline as readline

from _completer import Completer
from _completion import Completion
from _history import History

# Interface objects
completer = Completer()
completion = Completion()
history = History()

# Patch cmd.Cmd to use rl instead of readline
import _cmd


def generator(compfunc):
    """Generator function factory.

    Takes a function returning matches and returns an
    object implementing the generator protocol readline expects.
    The function will be called as ``compfunc(text)`` and should
    return an iterable of matches for ``text``.
    """
    class GeneratorFunction(object):

        def __call__(self, text, state):
            if state == 0:
                self.matches = compfunc(text)
                if not isinstance(self.matches, list):
                    self.matches = list(self.matches)
            try:
                return self.matches[state]
            except IndexError:
                return None

    return GeneratorFunction()


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


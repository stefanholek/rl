"""Alternative readline interface focusing on completion."""

from _stdlib import readline # [sic]
import _readline as readline

from _completer import completer
from _completion import completion
from _history import history

# For subclassing
from _completer import Completer
from _completion import Completion
from _history import History

# Patch cmd.Cmd to use rl instead of readline
import _cmd


class _GeneratorFunction(object):
    """Generator function implementation."""

    def __init__(self, compfunc):
        """Initialize the generator."""
        self.compfunc = compfunc

    def __call__(self, text, state):
        """Implement the generator protocol.

        Calls ``compfunc`` once, passing ``text`` as the only argument.
        Returns the resulting matches according to readline's generator
        protocol.
        """
        if state == 0:
            self.matches = self.compfunc(text)
            if not isinstance(self.matches, list):
                self.matches = list(self.matches)
        try:
            return self.matches[state]
        except IndexError:
            return None


def generator(compfunc):
    """Generator function factory.

    Takes a callable returning a list of matches and returns an
    object implementing the generator protocol readline requires.
    """
    return _GeneratorFunction(compfunc)


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


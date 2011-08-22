"""Global constants and utility functions."""

# Python uses these word break characters by default
DEFAULT_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


# Python 2 needs help importing global modules
import readline


# Python 3 has no apply
def apply(func, *args, **kw):
    """Call ``func`` with args and kwargs."""
    return func(*args, **kw)

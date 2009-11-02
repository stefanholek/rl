"""Python version compatibility hacks."""

# Python2 needs help importing global modules

import readline


# Python3 has no apply

def apply(func, *args, **kw):
    """Call ``func`` with args and kwargs."""
    return func(*args, **kw)

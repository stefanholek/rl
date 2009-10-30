"""Python3 compatibility."""

def apply(func):
    """Python3 has no ``apply``."""
    return func()

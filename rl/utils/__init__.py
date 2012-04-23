"""Global constants."""

# Python uses these word break characters by default
DEFAULT_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


# Python 2 needs help importing global modules
try:
    import readline
except ImportError:
    pass

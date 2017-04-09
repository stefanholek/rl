"""Global constants."""

# Python uses these word break characters by default
DEFAULT_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


# Python 3 has no apply
def apply(object, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    return object(*args, **kwargs)

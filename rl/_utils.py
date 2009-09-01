"""Generator function implementation."""


class GeneratorFunction(object):
    """Generator function implementation.

    The ``generator`` factory returns objects of this type.
    """

    def __init__(self, compfunc):
        """Initialize the generator.

        The passed-in function will be called as ``compfunc(text)``
        and should return an iterable of matches for ``text``.
        """
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


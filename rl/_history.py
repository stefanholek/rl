"""Interface to readline history."""

import _readline as readline


class History(object):
    """Interface to readline history.

    This class is not intended for instantiation beyond
    the one ``history`` object in this module.
    Applications wanting to use the History interface will
    typically import the ``history`` object and use its
    properties and methods to work with readline history.

    Example::

        from rl import history
        import atexit

        history.read_file(histfile)
        history.length = 100
        atexit.register(history.write_file, histfile)
    """

    def __init__(self):
        """Set ``base=0``."""
        # This is a-ok until we implement stifling (if ever)
        self.base = 0

    @property
    def current_length(self):
        """The current length of history."""
        return readline.get_current_history_length()

    def __len__(self):
        """Alias for ``current_length``."""
        return self.current_length

    @apply
    def base():
        doc="""The logical "base" of the history list. Defaults to 0."""
        def get(self):
            return readline.get_history_base()
        def set(self, int):
            readline.set_history_base(int)
        return property(get, set, doc=doc)

    @apply
    def length():
        doc="""The number of lines saved to the history file."""
        def get(self):
            return readline.get_history_length()
        def set(self, int):
            readline.set_history_length(int)
        return property(get, set, doc=doc)

    def clear(self):
        """Clear the current readline history."""
        readline.clear_history()

    def add_item(self, line):
        """Add a line to the history."""
        readline.add_history(line)

    def append(self, line):
        """Alias for ``add_item``."""
        self.add_item(line)

    def get_item(self, pos):
        """Return the contents of history at pos (zero-based)."""
        return readline.get_history_item(pos)

    def __getitem__(self, pos):
        """Alias for ``get_item``."""
        return self.get_item(pos)

    def remove_item(self, pos):
        """Remove a history item given by its position (zero-based)."""
        readline.remove_history_item(pos)

    def __delitem__(self, pos):
        """Alias for ``remove_item``."""
        self.remove_item(pos)

    def replace_item(self, pos, line):
        """Replace a history item given by its position with contents of line (zero-based)."""
        readline.replace_history_item(pos, line)

    def __setitem__(self, pos, line):
        """Alias for ``replace_item``."""
        self.replace_item(pos, line)

    def read_file(self, filename=None, raise_exc=False):
        """Load a readline history file. The default filename is ~/.history."""
        self._file_op(readline.read_history_file, filename, raise_exc)

    def write_file(self, filename=None, raise_exc=False):
        """Save a readline history file. The default filename is ~/.history."""
        self._file_op(readline.write_history_file, filename, raise_exc)

    def _file_op(self, op, filename, raise_exc):
        """Perform a file operation optionally ignoring IOErrors."""
        try:
            if filename:
                op(filename)
            else:
                op()
        except IOError:
            if raise_exc:
                raise

history = History()


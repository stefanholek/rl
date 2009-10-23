"""Interface to the readline history."""

import _readline as readline
from _py3compat import apply


class History(object):
    """Interface to the readline history.

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

    __slots__ = ()

    @property
    def _base(self):
        """The logical base of the history list."""
        return readline.get_history_base()

    @apply
    def length():
        doc="""The number of lines saved in the history file. A negative
        value means no limit. Defaults to -1."""
        def get(self):
            return readline.get_history_length()
        def set(self, int):
            readline.set_history_length(int)
        return property(get, set, doc=doc)

    def __len__(self):
        """The current history length."""
        return readline.get_current_history_length()

    def clear(self):
        """Clear the history."""
        readline.clear_history()

    def append(self, line):
        """Append a line to the history."""
        readline.add_history(line)

    def __getitem__(self, index):
        """Return the history item at index."""
        return readline.get_history_item(self._base + self._norm_index(index))

    def __delitem__(self, index):
        """Remove the history item at index."""
        readline.remove_history_item(self._norm_index(index))

    def __setitem__(self, index, line):
        """Replace the history item at index."""
        readline.replace_history_item(self._norm_index(index), line)

    # Alternative API
    add_item = append
    get_item = __getitem__
    remove_item = __delitem__
    replace_item = __setitem__

    def _norm_index(self, index):
        """Support negative indexes."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError('an integer is required')
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError('history index out of range')
        return index

    def read_file(self, filename=None, raise_exc=False):
        """Load a readline history file. The default filename is ~/.history."""
        self._file_op(readline.read_history_file, filename, raise_exc)

    def write_file(self, filename=None, raise_exc=False):
        """Save a readline history file. The default filename is ~/.history."""
        self._file_op(readline.write_history_file, filename, raise_exc)

    def _file_op(self, op, filename, raise_exc):
        """Perform a file operation optionally suppressing IOErrors."""
        try:
            if filename:
                op(filename)
            else:
                op()
        except IOError:
            if raise_exc:
                raise

history = History()


"""Readline history support."""

from rl import readline
from rl.utils import apply


class History(object):
    """Interface to the readline history.

    This class is not intended for instantiation beyond
    the one ``history`` object in this module.
    Applications wanting to use the History interface will
    typically import the ``history`` object and use its
    properties and methods to work with readline history.

    Example::

        from rl import history

        history.max_entries = 300
        history.read_file(histfile)

    History entries can be accessed like elements of a Python list.
    The item at index 0 is the oldest, the item at -1 the most recent
    history item.
    """

    __slots__ = ()

    @apply
    def max_entries():
        doc="""The maximum number of history entries kept. Beyond this
        point the history list is truncated by removing the oldest entry.
        A negative value means no limit. Defaults to -1."""
        def get(self):
            if readline.history_is_stifled():
                return readline.get_history_max_entries()
            return -1
        def set(self, int):
            if int < 0:
                readline.unstifle_history()
            else:
                readline.stifle_history(int)
        return property(get, set, doc=doc)

    def clear(self):
        """Clear the history."""
        readline.clear_history()

    def append(self, line):
        """Append a line to the history."""
        readline.add_history(line)

    def __getitem__(self, index):
        """Return the history item at index."""
        return readline.get_history_item(self._norm_index(index))

    def __delitem__(self, index):
        """Remove the history item at index."""
        readline.remove_history_item(self._norm_index(index))

    def __setitem__(self, index, line):
        """Replace the history item at index."""
        readline.replace_history_item(self._norm_index(index), line)

    def __len__(self):
        """The current history length."""
        return readline.get_current_history_length()

    def __iter__(self):
        """Iterate over history items."""
        return iter(readline.get_history_list())

    def __reversed__(self):
        """Reverse-iterate over history items."""
        return reversed(readline.get_history_list())

    def read_file(self, filename=None, raise_exc=False):
        """Load a readline history file. The default filename is ~/.history."""
        self._file_op(readline.read_history_file, filename, raise_exc)

    def write_file(self, filename=None, raise_exc=False):
        """Save a readline history file. The default filename is ~/.history."""
        self._file_op(readline.write_history_file, filename, raise_exc)

    def _norm_index(self, index):
        """Support negative indexes."""
        if not isinstance(index, int):
            raise TypeError('an integer is required')
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError('history index out of range')
        return index

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


"""Readline history support."""

from rl import readline
from rl.utils import apply

try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)


class History(object):
    """Interface to the readline history.
    Used to read and write history files and to manipulate history entries.

    This class is not intended for instantiation beyond
    the one :obj:`history <rl.History>` object in this module.
    Typically, applications will import the :obj:`history <rl.History>`
    object and use its properties and methods to work with
    readline history::

        from rl import history

        history.max_entries = 300
        history.read_file(histfile)

    History entries can be accessed like elements in a Python list.
    The item at index 0 is the oldest, the item at -1 the most recent
    history entry.
    """

    __slots__ = ()

    @apply
    def auto():
        doc="""Controls whether readline automatically adds lines to
        the history. Defaults to True. Set to False if you want to call
        :meth:`~rl.History.append` yourself."""
        def get(self):
            return readline.get_auto_history()
        def set(self, bool):
            readline.set_auto_history(bool)
        return property(get, set, doc=doc)

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

    @apply
    def max_file():
        doc="""The maximum size of a readline history file, in entries.
        Beyond this point the history file is truncated by removing the
        oldest entries. A negative value means no limit. Defaults to -1."""
        def get(self):
            return readline.get_history_length()
        def set(self, int):
            readline.set_history_length(max(int, -1))
        return property(get, set, doc=doc)

    def append(self, line):
        """Append a line to the history."""
        readline.add_history(line)

    def __getitem__(self, index):
        """Return the history item at index."""
        return readline.get_history_item(self._norm_index(index))

    def __setitem__(self, index, line):
        """Replace the history item at index."""
        readline.replace_history_item(self._norm_index(index), line)

    def __delitem__(self, index):
        """Remove the history item at index."""
        readline.remove_history_item(self._norm_index(index))

    def __len__(self):
        """The current history length."""
        return readline.get_current_history_length()

    def __iter__(self):
        """Iterate over history items (old to new)."""
        return readline.get_history_iter()

    def __reversed__(self):
        """Reverse-iterate over history items (new to old)."""
        return readline.get_history_reverse_iter()

    def clear(self):
        """Clear the history."""
        readline.clear_history()

    def read_file(self, filename=None, raise_exc=False):
        """Load a readline history file.
        The default filename is ~/.history. If ``raise_exc`` is True,
        IOErrors will be allowed to propagate.
        """
        try:
            readline.read_history_file(filename)
        except IOError:
            if raise_exc:
                raise

    def write_file(self, filename=None, raise_exc=False):
        """Save a readline history file.
        The default filename is ~/.history. If ``raise_exc`` is True,
        IOErrors will be allowed to propagate.
        """
        try:
            readline.write_history_file(filename)
        except IOError:
            if raise_exc:
                raise

    def append_file(self, numitems, filename=None, raise_exc=False):
        """Append the last ``numitems`` history entries to a readline history file.
        The default filename is ~/.history. If ``raise_exc`` is True,
        IOErrors will be allowed to propagate.
        """
        try:
            readline.append_history_file(numitems, filename)
        except IOError:
            if raise_exc:
                raise

    # Helpers

    def reset(self):
        """Clear the history and reset all variables to their built-in
        defaults. Used in tests."""
        self.clear()
        self.auto = True
        self.max_entries = -1
        self.max_file = -1

    def _norm_index(self, index):
        """Support negative indexes."""
        if isinstance(index, slice):
            raise TypeError('history cannot be sliced')
        if not isinstance(index, integer_types):
            raise TypeError('an integer is required')
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError('history index out of range')
        return index

history = History()


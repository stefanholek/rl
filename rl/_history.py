"""Readline history support."""

import sys

from rl import readline
from rl.utils import apply


class History(object):
    """Interface to the readline history.

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
    history entry::

        if current != history[-1]:
            history.append(current)
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

    def __len__(self):
        """The current history length."""
        return readline.get_current_history_length()

    def __getitem__(self, index):
        """Return the history item at index."""
        return readline.get_history_item(self._norm_index(index))

    def __setitem__(self, index, line):
        """Replace the history item at index."""
        readline.replace_history_item(self._norm_index(index), line)

    def __delitem__(self, index):
        """Remove the history item at index."""
        readline.remove_history_item(self._norm_index(index))

    def __iter__(self):
        """Iterate over history items."""
        #return iter(readline.get_history_list())
        return HistoryIterator(self)

    def __reversed__(self):
        """Reverse-iterate over history items."""
        #return reversed(readline.get_history_list())
        return HistoryReverseIterator(self)

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

    # Helpers

    def reset(self):
        """Clear the history and reset all variables to their default values."""
        self.clear()
        self.max_entries = -1

    def _norm_index(self, index):
        """Support negative indexes."""
        if not isinstance(index, (int, long)):
            raise TypeError('an integer is required')
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError('history index out of range')
        return index

history = History()


class HistoryIterator(object):

    def __init__(self, history):
        self.history = history
        self.index = 0

    def __next__(self):
        if self.index < len(self.history):
            item = self.history[self.index]
            self.index += 1
            return item
        raise StopIteration()

    if sys.version_info[0] < 3:
        next = __next__

    def __iter__(self):
        return self

    def __length_hint__(self):
        return len(self.history)


class HistoryReverseIterator(object):

    def __init__(self, history):
        self.history = history
        self.index = len(history) - 1

    def __next__(self):
        if 0 <= self.index < len(self.history):
            item = self.history[self.index]
            self.index -= 1
            return item
        raise StopIteration()

    if sys.version_info[0] < 3:
        next = __next__

    def __iter__(self):
        return self

    def __length_hint__(self):
        return len(self.history)


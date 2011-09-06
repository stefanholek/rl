"""Alternative Python bindings for GNU Readline.

Package contents
================

rl exports the following components:

:class:`rl.completer <rl._completion.Completer>`
    Interface to the readline completer.

:class:`rl.completion <rl._completion.Completion>`
    Interface to the active readline completion.

:func:`rl.generator() <rl._completion.generator>`
    Generator function factory.

:func:`rl.print_exc() <rl._completion.print_exc>`
    Decorator printing exceptions to stderr.

:class:`rl.history <rl._history.History>`
    Interface to the readline history.

:mod:`rl.readline`
    Readline bindings module.

Readline completion
=========================

Completion is the process initiated when the user presses the TAB key.
It has three phases: Word breaking, match generation, and
match display.

For each phase, readline provides configuration settings and hooks that
allow applications to control the way the library behaves. See the
:class:`~rl._completion.Completer` and :class:`~rl._completion.Completion`
classes for detailed descriptions of available properties.

Call graph
----------

A calling sequence for filename completion may look like this:

* :func:`complete_internal`

    * :func:`find_completion_word`

        * :attr:`~rl._completion.Completer.word_break_hook`

        * :attr:`~rl._completion.Completer.char_is_quoted_function`

    * :func:`gen_completion_matches`

        * :attr:`~rl._completion.Completer.completer`

            * :meth:`~rl._completion.Completion.complete_filename`

                * :attr:`~rl._completion.Completer.directory_completion_hook`

                * :attr:`~rl._completion.Completer.filename_dequoting_function`

        * :attr:`~rl._completion.Completer.ignore_some_completions_function`

    * :func:`insert_match`

        * :attr:`~rl._completion.Completer.filename_quoting_function`

    * :func:`display_matches`

        * :attr:`~rl._completion.Completer.display_matches_hook`

            * :meth:`~rl._completion.Completion.display_match_list`

Readline history
======================

History allows readline to save and later recall lines the user has entered.
The ``history`` object (of class :class:`~rl._history.History`) provides a
list-like interface to the history buffer as well as functions to persist the
history between sessions.

Upstream documentation
======================

The `GNU Readline Library`_ and the `GNU History Library`_.

.. _`GNU Readline Library`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44
.. _`GNU History Library`: http://tiswww.case.edu/php/chet/readline/history.html#SEC6
"""

# Grab the ReadlineFunctionPointer
import rl.utils
import rl.readline

# For subclassing (and epydoc)
from rl._completion import Completer
from rl._completion import Completion
from rl._history import History

# API
from rl._completion import completer
from rl._completion import completion
from rl._completion import generator
from rl._completion import print_exc
from rl._history import history

"""Python bindings for GNU Readline.

Package Contents
================

rl exports the following components:

completer
    Interface to the readline completer.

completion
    Interface to the active readline completion.

generator
    Generator function factory.

print_exc
    Decorator printing exceptions to stderr.

history
    Interface to the readline history.

readline
    Readline bindings module.

About Readline Completion
=========================

Completion is the process initiated when the user presses the TAB key.
It has three phases: 1) word breaking, 2) match generation, and
3) match display.

For each phase, readline provides configuration settings and hooks that
allow applications to control the way the library behaves. See the
`Completer` and `Completion` classes for detailed descriptions of available
properties.

Call Graph
----------

A calling sequence for filename completion may look like this:

* complete_internal

    * find_completion_word

        * `Completer.word_break_hook`

        * `Completer.char_is_quoted_function`

    * gen_completion_matches

        * `Completer.completer`

            * `Completion.complete_filename`

                * `Completer.directory_completion_hook`

                * `Completer.filename_dequoting_function`

        * `Completer.ignore_some_completions_function`

    * insert_match

        * `Completer.filename_quoting_function`

    * display_matches

        * `Completer.display_matches_hook`

            * `Completion.display_match_list`

About Readline History
======================

History allows readline to save and later recall lines the user has entered.
The ``history`` object (of class `History`) provides a list-like interface
to the history buffer as well as functions to persist the history
between sessions.

Upstream Documentation
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

# Patch cmd.Cmd to use rl instead of readline
import rl._cmd

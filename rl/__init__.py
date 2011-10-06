"""Alternative Python bindings for GNU Readline.

Package Contents
================

rl exports the following components:

:obj:`rl.completer <rl.Completer>`
    Interface to the readline completer. Used to configure the completion
    aspects of readline.

:obj:`rl.completion <rl.Completion>`
    Interface to the active readline completion. Used to interact
    with readline when a completion is in progress.

:obj:`rl.history <rl.History>`
    Interface to the readline history. Used to read and write history files
    and to manipulate history entries.

:mod:`rl.readline`
    The readline bindings module. Contains everything known from the standard
    library plus extensions specific to the rl package.  The :obj:`completer <rl.Completer>`,
    :obj:`completion <rl.Completion>`, and :obj:`history <rl.History>`
    objects make use of this module, and you should rarely need to interact
    with it directly.

:func:`rl.generator`
    A factory turning any callable into a *completion entry function* that
    can be handed to readline.

:func:`rl.print_exc`
    A decorator printing exceptions to stderr. Useful when writing Python
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

Readline Completion
===================

Completion is the process initiated when the user presses the TAB key.
It has three phases: Word breaking, match generation, and
match display.

For each phase, readline provides configuration settings and hooks that
allow applications to control the way the library behaves. See the
:class:`~rl.Completer` and :class:`~rl.Completion`
classes for detailed descriptions of available properties.

Call Graph
----------

A calling sequence for filename completion may look like this:

* :func:`complete_internal`

    * :func:`find_completion_word`

        * :attr:`~rl.Completer.word_break_hook`

        * :attr:`~rl.Completer.char_is_quoted_function`

    * :func:`gen_completion_matches`

        * :attr:`~rl.Completer.completer`

            * :meth:`~rl.Completion.complete_filename`

                * :attr:`~rl.Completer.directory_completion_hook`

                * :attr:`~rl.Completer.filename_dequoting_function`

        * :attr:`~rl.Completer.ignore_some_completions_function`

    * :func:`insert_match`

        * :attr:`~rl.Completer.filename_quoting_function`

    * :func:`display_matches`

        * :attr:`~rl.Completer.display_matches_hook`

            * :meth:`~rl.Completion.display_match_list`

Readline History
================

History allows readline to save and later recall lines the user has entered.
The :obj:`history <rl.History>` object provides a list-like interface to the
history buffer as well as functions to persist the history between sessions.
"""

# Upstream Documentation
# ======================
#
# The `GNU Readline Library`_ and the `GNU History Library`_.
#
# .. _`GNU Readline Library`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44
# .. _`GNU History Library`: http://tiswww.case.edu/php/chet/readline/history.html#SEC6

# Grab the ReadlineFunctionPointer
import rl.utils
import rl.readline

# For subclassing
from rl._completion import Completer
from rl._completion import Completion
from rl._history import History

# API
from rl._completion import completer
from rl._completion import completion
from rl._completion import generator
from rl._completion import print_exc
from rl._history import history

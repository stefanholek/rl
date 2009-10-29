"""Alternative readline interface focusing on completion.

Package Contents
================

rl exports the following components:

completer
    Interface to the readline completer. Used to configure the completion
    aspects of readline.

completion
    Interface to the active readline completion. Used to interact with
    readline when a completion is in progress.

history
    Interface to the readline history. Used to read and write history files
    and to manipulate history entries.

readline
    Basic readline interface module.

generator
    Generator function factory.

print_exc
    Decorator printing exceptions to stderr.

Readline Completion
===================

Completion is what happens when the user presses the TAB key.
It has 3 phases:

1. Word breaking

2. Match generation

3. Match display

For each phase, readline provides configuration settings and hooks that
allow applications to control the way the library behaves. See the
`Completer` and `Completion` classes for detailed descriptions of available
properties.

Call Graph
----------

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

Readline History
================

History allows readline to save and recall lines the user has entered.
The 'history' object (of class `History`) provides a list-like interface to
the history buffer as well as functions to persist the history
between sessions.

Upstream Documentation
======================

The GNU Readline Library documentation:
http://tiswww.case.edu/php/chet/readline/readline.html#SEC44
"""

# Grab the ReadlineFunctionPointer
import readline
import _readline as readline

# Patch cmd.Cmd to use rl instead of readline
import _cmd

# For subclassing
from _completion import Completer
from _completion import Completion
from _history import History

# API
from _completion import completer
from _completion import completion
from _completion import generator
from _completion import print_exc
from _history import history

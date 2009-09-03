==
rl
==
------------------------------------------------
Python readline interface focusing on completion
------------------------------------------------

Introduction
============

The rl package aims to provide a full implementation of the
GNU Readline `completion interface`_.

.. _`completion interface`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44

Readline Completion
===================

Call Graph
----------

* complete_internal

    * find_completion_word

        * **word_break_hook**

        * **char_is_quoted_function**

    * gen_completion_matches

        * **completion_entry_function**'*'

            * `filename_completion_function`

                * **directory_completion_hook**

                * **filename_dequoting_function**

    * insert_match

        * **filename_quoting_function**

    * display_matches

            * **display_matches_hook**

                * `display_match_list`

Discussion
----------

The graph – when read from top to bottom – represents a possible calling
sequence for filename completion in readline. This sequence is initiated
whenever the user presses the TAB key and has three phases:
word breaking, match generation, and match presentation.

Functions in **boldface** may be overridden by applications.
Functions in `italics` may be called by such application-provided hooks to
use functionality implemented in readline.

At C-level, there is a default ``filename_quoting_function`` and a default
``display_matches_hook``. The remaining hooks have no default implementations.

The ``completion_entry_function``, marked with an '*' above, has traditionally
been the place where Python hooks into readline. In fact, the standard
library's ``set_completer(func)`` sets readline's
``rl_completion_entry_function`` to ``func``. [#]_

In addition to hooks, readline provides an abundance of configuration
settings that may be changed by applications to influence the way the library
behaves. For example, by configuring readline's ``word_break_characters``, an
application can affect how readline computes word boundaries.

.. [#] This is not entirely correct. What it really does, is arrange
   things so that the readline C-library calls the Python function ``func``
   when generating matches. The effect however is the same as if ``func`` had
   been assigned to ``rl_completion_entry_function`` directly.

The rl Package
==============

Overview
--------

The rl package implements all flags, settings, and hooks documented in
the `Custom Completers`_ section of the `GNU Readline Library`_ manual.
They are presented to the user in the form of properties on two
interface objects, ``completer`` and ``completion``.

While names have been shortened – we removed the ``rl_`` prefix and the
occasional ``completer`` and ``completion`` from the C identifiers – they
should still be easy to recognize for anyone familiar with readline.

.. _`Custom Completers`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44
.. _`GNU Readline Library`: http://tiswww.case.edu/php/chet/readline/readline.html

Divide and Conquer
------------------

For the sake of abstraction we postulate a `completer` component in readline. It is
responsible for configuring and executing readline completions.

Secondly, we define a `completion` interface which is used by
applications to implement custom completion code.

The ``completer`` object
provides access to global configuration settings and hooks.

The ``completion``
object provides status information for the active completion,
configuration settings that affect the results of the completion, and
functions to use completion services implemented by readline.

Values set trough the ``completer`` are permanent. If you want
them restored you have to take care of it yourself.
Values accessed through the ``completion`` object affect the current
completion only. They are reset to their default values when a new
completion starts.

For further details, please refer to the `API Documentation`_.

.. _`API Documentation`: http://packages.python.org/rl/

Package Contents
----------------

rl exports the following components:

completer
    Interface to the readline completer. Used to configure the completion
    aspects of readline.

completion
    Interface to the active readline completion. Used to interact
    with readline when a completion is in progress.

history
    Interface to the readline history. Used to read and write history files
    and to manipulate history entries.

readline
    The readline module. Contains everything known from the standard library
    plus extensions specific to the rl package.  The ``completer``,
    ``completion``, and ``history`` interfaces make use of this module, and
    you should rarely need to interact with it directly.

generator
    A factory turning any callable into a ``completion_entry_function`` that
    can be handed to readline.

print_exc
    A decorator printing exceptions to stderr. Useful when writing Python
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

Example Code
------------

The code below implements system command completion similar to bash::

    import os
    from rl import completer
    from rl import generator

    def complete(text):
        # Return an iterable of matches for 'text'
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            yield name

    def main():
        # Set the completion function
        completer.completer = generator(complete)

        # Enable TAB completion
        completer.parse_and_bind('tab: complete')

        command = raw_input('command: ')
        print 'You typed:', command

See the ``examples`` subdirectory of the package for more.

Installation
============

On Linux, install libreadline5-dev (or equivalent) before attempting to build
rl. On Mac OS X, you need a Python built with MacPorts or Fink, as the system
Python is linked to the BSD editline library and not GNU readline.

Then type::

    /path/to/easy_install rl

and watch the console. When it reads::

    Finished processing dependencies for rl

you are done and rl is ready to use.


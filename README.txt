==========
completion
==========
------------------------------------------------
Python readline interface focusing on completion
------------------------------------------------

Introduction
============

The completion package aims to provide a full implementation of the
GNU Readline `completion interface`_.

.. _`completion interface`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44

How Readline Completion Works
=============================

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

Readline Completion
-------------------

The graph – when read from top to bottom – represents a possible calling
sequence for filename completion in readline. This sequence is initiated
whenever the user presses the TAB key and has three phases:
word breaking, match generation, and match display.

Functions in **boldface** may be overridden by applications.
Functions in `italics` may be called by such application-provided hooks to
pass control back to readline.

At C-level, there is a default ``filename_quoting_function`` and a default
``display_matches_hook``. The remaining hooks have no default implementations.

The ``completion_entry_function``, marked with an '*' above, has traditionally
been the place where Python hooks into readline. In fact,
``readline.set_completer(func)`` sets readline's
``[rl_]completion_entry_function`` to ``func``. [#]_

In addition to these hooks, readline provides an abundance of configuration
settings that may be changed by applications to influence the way the library
behaves. For example, by configuring readline's ``word_break_characters``, an
application can affect how readline computes word boundaries.

.. [#] This is not entirely correct. What it really does, is arrange
   things so that the readline C-library calls the Python function ``func``
   when generating matches. The effect however is the same as if ``func`` had
   been assigned to ``[rl_]completion_entry_function`` directly.

Custom Completers
-----------------

[TBD]

The completion Package
======================

Overview
--------

The completion package implements all flags, settings, and hooks documented in
the `Custom Completers`_ section of the `GNU Readline Library`_ manual.
They are presented to the user in the form of properties on two
interface objects, ``completer`` and ``completion``.

While names have been shortened – we removed the ``rl_`` prefix and the
occasional ``completer`` or ``completion`` from the C identifiers – they
should still be easily recognizable by anyone familiar with readline.

.. _`Custom Completers`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44
.. _`GNU Readline Library`: http://tiswww.case.edu/php/chet/readline/readline.html

Package Contents
----------------

completer
    Interface to the readline completer. Used to configure the completion
    aspects of readline.

completion
    Interface to the active readline completion. Used to interact
    with readline when a completion is in progress.

readline
    The readline interface module. Contains everything
    known from the standard library plus extensions specific to the
    completion package. The ``completer`` and ``completion`` interfaces make use of
    this module, and you should rarely need to interact with it directly.

cmd
    A subclass of ``cmd.Cmd`` using completion's version of readline.

generator
    A factory turning a callable into a ``completion_entry_function`` that
    can be handed to readline.

print_exc
    A decorator printing exceptions to stderr. Useful when writing Python
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

Divide and Conquer
------------------

Readline's completion interface is massive, so we break it down into two
interface objects:

completer
    16 properties (7 configuration settings, 9 hooks) and 2 functions.

completion
    16 properties (4 status flags, 7 completion settings, 5 completion
    variables) and 4 functions.

On the one hand, this separation is by concern: The ``completer`` provides
access to global configuration settings and hooks. The ``completion`` interface
provides status information concerning the active completion, configuration
settings to affect the results of the completion, and
functions to request services implemented by readline.

On the other hand, it is also a separation by value lifetime:
Values set trough the ``completer`` are global and permanent. If you want
them restored you have to take care of it yourself.
Values accessed through the ``completion`` object affect the current
completion only. They are reset to their default values when a new
completion starts.

For further details, please refer to the `API Documentation`_.

.. _`API Documentation`: http://packages.python.org/completion/

Example
-------

The code below implements system command completion similar to bash::

    import os
    from completion import completer
    from completion import generator

    def complete(text):
        for dir in os.environ.get('PATH').split(':'):
            for name in os.listdir(dir):
                if name.startswith(text):
                    if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                        yield name

    def main():
        completer.completer = generator(complete)
        completer.parse_and_bind('tab: complete')
        command = raw_input('command> ')
        print 'You typed:', command

See the ``examples`` subdirectory of the package for more.

Installation
============

On Linux, install libreadline5-dev (or equivalent) before attempting to build
completion. On Mac OS X, you need a Python built with MacPorts or Fink, as
the system Python is linked to the BSD editline library and not GNU readline.

Then type::

    /path/to/easy_install completion

and watch the console. When it reads::

    Finished processing dependencies for completion==1.0a1

you are done and completion is ready to use.


==
rl
==
--------------------------------------------
Alternative Python bindings for GNU Readline
--------------------------------------------

Overview
============

The `GNU Readline Library`_ is the canonical implementation of command line
editing, tab completion, and history for console-based applications.
It is developed as part of Bash and available on virtually any platform.

While Python ships with readline bindings in its standard library, they
only implement a subset of readline's features, just enough to perform
identifier completion at the Python interpreter prompt.

The **rl** package aims to provide full implementations of GNU Readline's
`Custom Completer`_ and `History`_ interfaces.
It also contains high-level APIs to better organize the namespace and
shield applications from low-level verbosity.

.. _`GNU Readline Library`: https://tiswww.case.edu/php/chet/readline/rltop.html
.. _`Custom Completer`: https://tiswww.case.edu/php/chet/readline/readline.html#SEC45
.. _`History`: https://tiswww.case.edu/php/chet/readline/history.html#SEC6

Package Contents
----------------

rl exports these components:

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
    The readline bindings module. Contains everything known from the standard
    library plus extensions specific to the rl package.  The *completer*,
    *completion*, and *history* interfaces make use of this module, and you
    should rarely need to interact with it directly.

generator
    A factory turning any callable into a *completion entry function* that
    can be handed to readline.

print_exc
    A decorator printing exceptions to stderr. Useful when writing Python
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

For further details please refer to the `API Documentation`_.

.. _`API Documentation`: https://rl.readthedocs.io/en/latest/

Example Code
------------

The code below implements system command completion similar to Bash::

    import os
    from rl import completer
    from rl import generator

    def complete_command(text):
        # Return executables matching 'text'
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            yield name

    def main():
        # Set the completion entry function
        completer.completer = generator(complete_command)

        # Enable TAB completion
        completer.parse_and_bind('TAB: complete')

        command = input('command> ')
        print('You typed:', command)

More examples_ are included in the package source.

.. _examples: https://github.com/stefanholek/rl/tree/master/rl/examples

Development
-----------

rl development is hosted on GitHub_ where it also has an `issue tracker`_.

.. _GitHub: https://github.com/stefanholek/rl
.. _`issue tracker`: https://github.com/stefanholek/rl/issues

Installation
============

rl requires Python 2.6 or higher and GNU Readline 5.0 or higher.

On Linux, install libreadline6-dev before attempting to build
rl. On Mac OS X, make sure you have Xcode Tools installed. Then type::

    pip install rl

Static Builds
-------------

Normally, rl.readline will attempt to link against your system's libreadline.
If this is not possible, notably on Mac OS X which ships with libedit, a
static version of GNU Readline 6.3 is built.

To force a static build, set the RL_BUILD_STATIC_READLINE environment
variable.


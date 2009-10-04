==
rl
==
------------------------------------------------
Python readline interface focusing on completion
------------------------------------------------

Introduction
============

The rl package aims to provide a full implementation of the
GNU Readline `Custom Completer`_ interface.

.. _`Custom Completer`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44

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
    The readline interface module. Contains everything known from the standard
    library plus extensions specific to the rl package.  The `completer`,
    `completion`, and `history` interfaces make use of this module, and
    you should rarely need to interact with it directly.

generator
    A factory turning any callable into a `completion entry function` that
    can be handed to readline.

print_exc
    A decorator printing exceptions to stderr. Useful when writing Python
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

For further details, please refer to the `API Documentation`_.

.. _`API Documentation`: http://packages.python.org/rl/

Example Code
------------

The code below implements system command completion similar to bash::

    import os
    from rl import completer
    from rl import generator

    def complete(text):
        # Return executables matching 'text'
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

rl has been tested with GNU Readline versions 5 and 6.

On Linux, install libreadline5-dev (or equivalent) before attempting to build
rl. On Mac OS X, you need a Python built with MacPorts or Fink, as the system
Python is linked to the BSD editline library and not GNU readline.

rl requires distribute >= 0.6.3. If you have not upgraded from setuptools
yet, type::

    /path/to/easy_install distribute

Then type::

    /path/to/easy_install rl

and watch the console. When it reads::

    Finished processing dependencies for rl

you are done and rl is ready to use.


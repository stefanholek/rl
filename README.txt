==========
completion
==========
-----------------------------------------------------------
Alternative Python readline interface focused on completion
-----------------------------------------------------------

Introduction
============

This module aims to provide a fully-featured implementation of the GNU
readline `completion interface`_.

.. _`completion interface`: http://tiswww.case.edu/php/chet/readline/readline.html#SEC44

How readline Completion Works
=============================

TBD

How completion Works
====================

Components
----------

completer
    Interface to the readline completer. Used to configure the completion
    aspects of readline.

completion
    Interface to the active readline completion. Used to interact
    with readline while a completion is in progress.

readline
    Bare-bones interface to the _readline.so C library. Contains everything
    known from the standard library, plus extensions specific to the
    `completion` package. The completer and completion interfaces make use of
    this module, and you should rarely need to interact with it directly.

cmd
    A subclass of cmd.Cmd using `completion`'s version of readline.

print_exc
    A decorator printing exceptions to stderr. Useful when writing (Python)
    completions and hooks, as exceptions occurring there are usually
    swallowed by the in-between C code.

Example Code
------------
::

    import os
    from completion import cmd

    class MyCmd(cmd.Cmd):

        def do_shell(self, args):
            """Usage: !command"""
            os.system(args)

        def complete_shell(self, text, *ignored):
            return self.completesys(text)

        def completesys(self, text):
            matches = []
            for dir in os.environ.get('PATH').split(':'):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            matches.append(name)
            return matches

Installation
============

On \*nix, install libreadline6-dev and libncurses5-dev (or equivalent) before
attempting to build `completion`. On Mac OS X you need a Python built with
MacPorts or Fink, as the system Python uses the BSD editline library and not
GNU readline.

Then type::

    easy_install completion

and watch the console for problems. Once it says::

    Finished processing dependencies for completion==1.0

you are done and `completion` is ready to use.


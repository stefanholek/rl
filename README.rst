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
================

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

Documentation
=============

For further details please refer to the `API Documentation`_.

.. _`API Documentation`: https://rl.readthedocs.io/en/stable/

Development
===========

rl development is hosted on GitHub_ where it also has an `issue tracker`_.

.. _GitHub: https://github.com/stefanholek/rl
.. _`issue tracker`: https://github.com/stefanholek/rl/issues

Installation
============

rl requires Python 2.7 or higher. The installer builds GNU Readline 8.0
and a Python extension module.

On Mac OS X make sure you have Xcode Tools installed. Open a Terminal
window and type::

    gcc --version

You either see some output (good) or an installer window pops up. Click
the "Install" button to install the command line developer tools.
A more detailed tutorial is available from `RailsApps`_.

On Linux and BSD systems you probably already have a C compiler, but you may
need to verify the development environment is complete.
For example, Ubuntu lacks the Python headers by default and base Fedora is
missing some compiler configuration. Lastly, readline needs a termcap library
to link to.

.. _`RailsApps`: https://railsapps.github.io/xcode-command-line-tools.html

Ubuntu/Debian::

    sudo apt install build-essential
    sudo apt install python3-dev
    sudo apt install libtinfo-dev

Redhat/Fedora::

    sudo dnf install gcc
    sudo dnf install redhat-rpm-config
    sudo dnf install ncurses-devel

Then type::

    pip install rl

Related
=======

`kmd.Kmd`_ is an rl-enabled version of `cmd.Cmd`_.

.. _`kmd.Kmd`: https://github.com/stefanholek/kmd
.. _`cmd.Cmd`: https://docs.python.org/3/library/cmd.html


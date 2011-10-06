==================
Example Code
==================

Introductory code examples.

Completion Function
===================

The completion entry function is called as ``function(text, state)`` for
state in 0, 1, 2, ... until it returns None. It should return the next
possible completion for ``text``:

.. literalinclude:: ../rl/examples/raw_input.py

Generator Factory
=================

The :func:`~rl.generator` factory provides a simpler way to support this
protocol:

.. literalinclude:: ../rl/examples/factory.py

Multiple Completions
====================

Most of the time the completion entry function is itself a dispatcher,
forwarding calls to more specific completion functions depending on
position and format of the completion word:

.. literalinclude:: ../rl/examples/email.py

Pre-Input Hook
==============

The :attr:`~rl.Completer.pre_input_hook` may be used to pre-populate
the line buffer:

.. literalinclude:: ../rl/examples/pre_input_hook.py


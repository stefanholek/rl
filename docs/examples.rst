===================
Examples
===================

.. module:: rl.examples

Example code.

Completion Entry Function
============================

The completion entry function is called as ``function(text, state)`` for
state in 0, 1, 2, ... until it returns None. It should return the next
possible completion for ``text``:

.. literalinclude:: ../rl/examples/raw_input.py

Generator Factory
====================

The :func:`~rl.generator` factory provides a simpler way to support this
protocol:

.. literalinclude:: ../rl/examples/factory.py

Multiple Completions
=======================

The completion entry function is often a dispatcher,
forwarding calls to more specific completion functions depending on
position and format of the completion word:

.. literalinclude:: ../rl/examples/email.py

Filename Completion
======================

Filename completion is readline's party trick. It is also the most complex
feature, requiring various parts of readline to be set up:

.. literalinclude:: ../rl/examples/filename.py

Display Matches Hook
=======================

The :attr:`~rl.Completer.display_matches_hook` is called whenever matches need
to be displayed:

.. literalinclude:: ../rl/examples/display_matches_hook.py


==================
Completion Support
==================

.. automodule:: rl._completion

Completer Interface
===================

.. autoclass:: rl.Completer

.. autoattribute:: rl.Completer.quote_characters
.. autoattribute:: rl.Completer.word_break_characters
.. autoattribute:: rl.Completer.special_prefixes
.. autoattribute:: rl.Completer.filename_quote_characters
.. autoattribute:: rl.Completer.inhibit_completion
.. autoattribute:: rl.Completer.query_items

.. autoattribute:: rl.Completer.completer

.. autoattribute:: rl.Completer.startup_hook
.. autoattribute:: rl.Completer.pre_input_hook

.. autoattribute:: rl.Completer.word_break_hook
.. autoattribute:: rl.Completer.char_is_quoted_function
.. autoattribute:: rl.Completer.filename_quoting_function
.. autoattribute:: rl.Completer.filename_dequoting_function

.. autoattribute:: rl.Completer.directory_completion_hook

.. autoattribute:: rl.Completer.ignore_some_completions_function
.. autoattribute:: rl.Completer.display_matches_hook

.. automethod:: rl.Completer.read_init_file
.. automethod:: rl.Completer.parse_and_bind

Additional hooks for when the filesystem representation differs from the representation in the terminal
-------------------------------------------------------------------------------------------------------

.. autoattribute:: rl.Completer.directory_rewrite_hook
.. autoattribute:: rl.Completer.filename_rewrite_hook
.. autoattribute:: rl.Completer.filename_stat_hook

Completion Interface
====================

.. autoclass:: rl.Completion

.. autoattribute:: rl.Completion.line_buffer

.. autoattribute:: rl.Completion.completion_type
.. autoattribute:: rl.Completion.begidx
.. autoattribute:: rl.Completion.endidx
.. autoattribute:: rl.Completion.found_quote
.. autoattribute:: rl.Completion.quote_character
.. autoattribute:: rl.Completion.suppress_quote
.. autoattribute:: rl.Completion.append_character
.. autoattribute:: rl.Completion.suppress_append
.. autoattribute:: rl.Completion.filename_completion_desired
.. autoattribute:: rl.Completion.filename_quoting_desired

.. automethod:: rl.Completion.complete_filename
.. automethod:: rl.Completion.complete_username

.. automethod:: rl.Completion.expand_tilde
.. automethod:: rl.Completion.display_match_list
.. automethod:: rl.Completion.redisplay

Functions
========================

.. autofunction:: rl.generator
.. autofunction:: rl.print_exc


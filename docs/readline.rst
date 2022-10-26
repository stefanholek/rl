=================
Readline Bindings
=================

.. automodule:: rl.readline

Readline Interface
===================

The :mod:`rl.readline` module is an API-compatible replacement for the standard
library's :mod:`readline <py3k:readline>` bindings.
The standard library documentation applies, with the following exceptions:

#. :func:`get_completion_type` returns a string.
#. :func:`get_completion_append_character` defaults to the space character.
#. :func:`get_history_item` is zero-based.
#. :func:`redisplay` accepts an optional ``force`` argument.

Beyond that, :mod:`rl.readline` adds a plethora of new functionality which is
typically accessed through the high-level interfaces :obj:`rl.completer <rl.Completer>`,
:obj:`rl.completion <rl.Completion>`, and :obj:`rl.history <rl.History>`.
Functions not exposed through a high-level interface:

- :func:`readline_version` returns the readline library version as an integer.
- :func:`read_key` reads a character from the keyboard.
- :func:`stuff_char` stuffs a character into the input stream.
- :func:`complete_internal` executes the completer. Used in tests.

.. note:: It is possible to use ``rl.readline`` without the high-level APIs.
   To switch an existing application to ``rl``, change occurrences of
   ``import readline`` to ``from rl import readline``.

.. note:: Applications must not use the standard library ``readline`` and
   ``rl.readline`` simultaneously. This is because only one module can own the
   ``PyOS_ReadlineFunctionPointer``.

Functions
===================

.. autofunction:: rl.readline.add_history
.. autofunction:: rl.readline.append_history_file
.. autofunction:: rl.readline.clear_history
.. autofunction:: rl.readline.complete_internal
.. autofunction:: rl.readline.display_match_list
.. autofunction:: rl.readline.filename_completion_function

.. autofunction:: rl.readline.get_auto_history
.. autofunction:: rl.readline.get_begidx
.. autofunction:: rl.readline.get_char_is_quoted_function

.. autofunction:: rl.readline.get_completer
.. autofunction:: rl.readline.get_completer_delims
.. autofunction:: rl.readline.get_completer_quote_characters

.. autofunction:: rl.readline.get_completion_append_character
.. autofunction:: rl.readline.get_completion_display_matches_hook
.. autofunction:: rl.readline.get_completion_found_quote
.. autofunction:: rl.readline.get_completion_query_items
.. autofunction:: rl.readline.get_completion_quote_character
.. autofunction:: rl.readline.get_completion_suppress_append
.. autofunction:: rl.readline.get_completion_suppress_quote
.. autofunction:: rl.readline.get_completion_type
.. autofunction:: rl.readline.get_completion_word_break_hook

.. autofunction:: rl.readline.get_current_history_length
.. autofunction:: rl.readline.get_directory_completion_hook
.. autofunction:: rl.readline.get_directory_rewrite_hook
.. autofunction:: rl.readline.get_endidx

.. autofunction:: rl.readline.get_filename_completion_desired
.. autofunction:: rl.readline.get_filename_dequoting_function
.. autofunction:: rl.readline.get_filename_quote_characters
.. autofunction:: rl.readline.get_filename_quoting_desired
.. autofunction:: rl.readline.get_filename_quoting_function
.. autofunction:: rl.readline.get_filename_rewrite_hook
.. autofunction:: rl.readline.get_filename_stat_hook

.. autofunction:: rl.readline.get_history_item
.. autofunction:: rl.readline.get_history_iter
.. autofunction:: rl.readline.get_history_length
.. autofunction:: rl.readline.get_history_list
.. autofunction:: rl.readline.get_history_max_entries
.. autofunction:: rl.readline.get_history_reverse_iter

.. autofunction:: rl.readline.get_ignore_some_completions_function
.. autofunction:: rl.readline.get_inhibit_completion
.. autofunction:: rl.readline.get_line_buffer
.. autofunction:: rl.readline.get_pre_input_hook
.. autofunction:: rl.readline.get_rl_end
.. autofunction:: rl.readline.get_rl_point
.. autofunction:: rl.readline.get_special_prefixes
.. autofunction:: rl.readline.get_startup_hook

.. autofunction:: rl.readline.history_is_stifled
.. autofunction:: rl.readline.insert_text
.. autofunction:: rl.readline.parse_and_bind
.. autofunction:: rl.readline.read_history_file
.. autofunction:: rl.readline.read_init_file
.. autofunction:: rl.readline.read_key
.. autofunction:: rl.readline.readline_version
.. autofunction:: rl.readline.redisplay

.. autofunction:: rl.readline.remove_history_item
.. autofunction:: rl.readline.replace_history_item
.. autofunction:: rl.readline.replace_line

.. autofunction:: rl.readline.set_auto_history
.. autofunction:: rl.readline.set_begidx
.. autofunction:: rl.readline.set_char_is_quoted_function

.. autofunction:: rl.readline.set_completer
.. autofunction:: rl.readline.set_completer_delims
.. autofunction:: rl.readline.set_completer_quote_characters

.. autofunction:: rl.readline.set_completion_append_character
.. autofunction:: rl.readline.set_completion_display_matches_hook
.. autofunction:: rl.readline.set_completion_found_quote
.. autofunction:: rl.readline.set_completion_query_items
.. autofunction:: rl.readline.set_completion_quote_character
.. autofunction:: rl.readline.set_completion_suppress_append
.. autofunction:: rl.readline.set_completion_suppress_quote
.. autofunction:: rl.readline.set_completion_type
.. autofunction:: rl.readline.set_completion_word_break_hook

.. autofunction:: rl.readline.set_directory_completion_hook
.. autofunction:: rl.readline.set_directory_rewrite_hook
.. autofunction:: rl.readline.set_endidx

.. autofunction:: rl.readline.set_filename_completion_desired
.. autofunction:: rl.readline.set_filename_dequoting_function
.. autofunction:: rl.readline.set_filename_quote_characters
.. autofunction:: rl.readline.set_filename_quoting_desired
.. autofunction:: rl.readline.set_filename_quoting_function
.. autofunction:: rl.readline.set_filename_rewrite_hook
.. autofunction:: rl.readline.set_filename_stat_hook

.. autofunction:: rl.readline.set_history_length

.. autofunction:: rl.readline.set_ignore_some_completions_function
.. autofunction:: rl.readline.set_inhibit_completion
.. autofunction:: rl.readline.set_pre_input_hook
.. autofunction:: rl.readline.set_special_prefixes
.. autofunction:: rl.readline.set_startup_hook

.. autofunction:: rl.readline.stifle_history
.. autofunction:: rl.readline.stuff_char
.. autofunction:: rl.readline.tilde_expand
.. autofunction:: rl.readline.unstifle_history
.. autofunction:: rl.readline.username_completion_function
.. autofunction:: rl.readline.write_history_file


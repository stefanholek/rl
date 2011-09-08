==================
Completion Support
==================

.. toctree::
   :maxdepth: 2

.. automodule:: rl._completion

Completer object
================

.. autoclass:: rl._completion.Completer

   .. autoattribute:: quote_characters
   .. autoattribute:: word_break_characters
   .. autoattribute:: special_prefixes
   .. autoattribute:: filename_quote_characters
   .. autoattribute:: inhibit_completion
   .. autoattribute:: query_items

   .. autoattribute:: completer
   .. autoattribute:: startup_hook
   .. autoattribute:: pre_input_hook
   .. autoattribute:: word_break_hook
   .. autoattribute:: directory_completion_hook
   .. autoattribute:: display_matches_hook
   .. autoattribute:: char_is_quoted_function
   .. autoattribute:: filename_quoting_function
   .. autoattribute:: filename_dequoting_function
   .. autoattribute:: ignore_some_completions_function

   .. automethod:: read_init_file
   .. automethod:: parse_and_bind
   .. automethod:: reset

Completion object
=================

.. autoclass:: rl._completion.Completion

   .. autoattribute:: line_buffer
   .. autoattribute:: completion_type
   .. autoattribute:: begidx
   .. autoattribute:: endidx
   .. autoattribute:: found_quote
   .. autoattribute:: quote_character
   .. autoattribute:: suppress_quote
   .. autoattribute:: append_character
   .. autoattribute:: suppress_append
   .. autoattribute:: filename_completion_desired
   .. autoattribute:: filename_quoting_desired
   .. autoattribute:: rl_point
   .. autoattribute:: rl_end

   .. automethod:: complete_filename
   .. automethod:: complete_username
   .. automethod:: expand_tilde
   .. automethod:: display_match_list
   .. automethod:: redisplay
   .. automethod:: reset

Functions
=========

.. autofunction:: generator
.. autofunction:: print_exc


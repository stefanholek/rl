"""Interface to the readline completer configuration."""

import sys
import _readline as readline


class Completer(object):
    """Interface to the readline completer configuration.

    This class is not intended for instantiation beyond
    the one ``completer`` object in this package.
    Applications wanting to use the Completer interface will
    typically import the ``completer`` object and use its
    properties and methods to configure readline.

    Example::

        from rl import completer

        completer.quote_characters = '"\\''
        completer.query_items = 100
        completer.parse_and_bind('tab: complete')
    """

    # For filename_quoting_function
    SINGLE_MATCH = 1
    MULT_MATCH = 2

    @apply
    def quote_characters():
        doc="""Characters that may be used in pairs to quote substrings
        of the line."""
        def get(self):
            return readline.get_completer_quote_characters()
        def set(self, string):
            readline.set_completer_quote_characters(string)
        return property(get, set, doc=doc)

    @apply
    def word_break_characters():
        doc="""Characters that define word boundaries (aka delimiters)."""
        def get(self):
            return readline.get_completer_delims()
        def set(self, string):
            readline.set_completer_delims(string)
        return property(get, set, doc=doc)

    @apply
    def special_prefixes():
        doc="""Characters that are word break characters but should
        be left in the word passed to the completer."""
        def get(self):
            return readline.get_special_prefixes()
        def set(self, string):
            readline.set_special_prefixes(string)
        return property(get, set, doc=doc)

    @apply
    def filename_quote_characters():
        doc="""Characters that trigger quoting of filenames."""
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            readline.set_filename_quote_characters(string)
        return property(get, set, doc=doc)

    @apply
    def match_hidden_files():
        doc="""If True, include hidden files when matching filenames."""
        def get(self):
            return readline.get_match_hidden_files()
        def set(self, bool):
            readline.set_match_hidden_files(bool)
        return property(get, set, doc=doc)

    @apply
    def tilde_expansion():
        doc="""If True, completion functions perform tilde expansion."""
        def get(self):
            return readline.get_complete_with_tilde_expansion()
        def set(self, bool):
            readline.set_complete_with_tilde_expansion(bool)
        return property(get, set, doc=doc)

    @apply
    def query_items():
        doc="""Up to this many items will be displayed in response to a
        possible-completions call. Beyond that the user is prompted if he
        really wants to see all matches. Defaults to 100. A negative value
        means never prompt. The prompt is bypassed when a custom
        ``display_matches_hook`` is installed."""
        def get(self):
            return readline.get_completion_query_items()
        def set(self, int):
            readline.set_completion_query_items(int)
        return property(get, set, doc=doc)

    @apply
    def completer():
        doc="""The completer function.
        The function is called as ``function(text, state)``, for state
        in 0, 1, 2, ..., until it returns a non-string. It should return the
        next possible completion starting with ``text``."""
        def get(self):
            return readline.get_completer()
        def set(self, function):
            readline.set_completer(function)
        return property(get, set, doc=doc)

    @apply
    def startup_hook():
        doc="""The startup hook function.
        The function is called with no arguments just before readline
        prints the first prompt."""
        def get(self):
            return readline.get_startup_hook()
        def set(self, function):
            readline.set_startup_hook(function)
        return property(get, set, doc=doc)

    @apply
    def pre_input_hook():
        doc="""The pre-input hook function.
        The function is called with no arguments after the first
        prompt has been printed and just before readline starts reading
        input characters."""
        def get(self):
            return readline.get_pre_input_hook()
        def set(self, function):
            readline.set_pre_input_hook(function)
        return property(get, set, doc=doc)

    @apply
    def word_break_hook():
        doc="""The word break hook function.
        The function is called as ``function(begidx, endidx)``
        once per completion and should return a string of word
        break characters for the scope of the completion, or None
        to indicate no change."""
        def get(self):
            return readline.get_completion_word_break_hook()
        def set(self, function):
            readline.set_completion_word_break_hook(function)
        return property(get, set, doc=doc)

    @apply
    def directory_completion_hook():
        doc="""The directory completion hook function.
        The function is called as ``function(dirname)`` and should
        return a new directory name or None to indicate no change."""
        def get(self):
            return readline.get_directory_completion_hook()
        def set(self, function):
            readline.set_directory_completion_hook(function)
        return property(get, set, doc=doc)

    @apply
    def display_matches_hook():
        doc="""The display matches hook function.
        The function is called as ``function(substitution, matches, longest_match_length)``
        once each time matches need to be displayed. It typically calls
        ``display_match_list`` to do the actual work."""
        def get(self):
            return readline.get_completion_display_matches_hook()
        def set(self, function):
            readline.set_completion_display_matches_hook(function)
        return property(get, set, doc=doc)

    @apply
    def char_is_quoted_function():
        doc="""The char-is-quoted function.
        The function is called as ``function(text, index)``
        and should return True if the character at ``index`` is quoted,
        False otherwise."""
        def get(self):
            return readline.get_char_is_quoted_function()
        def set(self, function):
            readline.set_char_is_quoted_function(function)
        return property(get, set, doc=doc)

    @apply
    def filename_quoting_function():
        doc="""The filename quoting function.
        The function is called as ``function(text, match_type, quote_char)``
        and should return a string representing a quoted version
        of ``text``, or None to indicate no change. The ``match_type``
        argument is set to either ``SINGLE_MATCH`` or ``MULT_MATCH``
        depending on the number of matches the completion has generated."""
        def get(self):
            return readline.get_filename_quoting_function()
        def set(self, function):
            readline.set_filename_quoting_function(function)
        return property(get, set, doc=doc)

    @apply
    def filename_dequoting_function():
        doc="""The filename dequoting function.
        The function is called as ``function(text, quote_char)``
        and should return a string representing a dequoted version of
        ``text``, or None to indicate no change."""
        def get(self):
            return readline.get_filename_dequoting_function()
        def set(self, function):
            readline.set_filename_dequoting_function(function)
        return property(get, set, doc=doc)

    # Configuration functions

    def read_init_file(self, filename):
        """Parse a readline initialization file."""
        return readline.read_init_file(filename)

    def parse_and_bind(self, line):
        """Parse one line of a readline initialization file."""
        return readline.parse_and_bind(line)

    # Debugging

    def _dump(self, stream=sys.stdout):
        """Dump properties to stream."""
        stream.write("""\
quote_characters:               %r
word_break_characters:          %r
special_prefixes:               %r
filename_quote_characters:      %r
match_hidden_files:             %s
tilde_expansion:                %s
query_items:                    %d
completer:                      %r
startup_hook:                   %r
pre_input_hook:                 %r
word_break_hook:                %r
directory_completion_hook:      %r
display_matches_hook:           %r
char_is_quoted_function:        %r
filename_quoting_function:      %r
filename_dequoting_function:    %r
""" % (
self.quote_characters,
self.word_break_characters,
self.special_prefixes,
self.filename_quote_characters,
self.match_hidden_files,
self.tilde_expansion,
self.query_items,
self.completer,
self.startup_hook,
self.pre_input_hook,
self.word_break_hook,
self.directory_completion_hook,
self.display_matches_hook,
self.char_is_quoted_function,
self.filename_quoting_function,
self.filename_dequoting_function,
))


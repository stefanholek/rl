"""Alternative readline interface focusing on completion."""

import sys

from stdlib import readline # [sic]
import readline

# Rein in runaway completions
_MAXMATCHES = 100000


class Completer(object):
    """Interface to the readline completer configuration.

    This class is not intended for instantiation beyond
    the one ``completer`` object in this module.
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
        doc="""Threshold above which the user is prompted if he really
        wants to see all matches. Defaults to 100."""
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
        The function is called as ``function(text, begidx, endidx)``
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
        once each time matches need to be displayed."""
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
        argument is set to either ``SINGLE_MATCH`` or ``MULT_MATCH``."""
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
completer.quote_characters,
completer.word_break_characters,
completer.special_prefixes,
completer.filename_quote_characters,
completer.match_hidden_files,
completer.tilde_expansion,
completer.query_items,
completer.completer,
completer.startup_hook,
completer.pre_input_hook,
completer.word_break_hook,
completer.directory_completion_hook,
completer.display_matches_hook,
completer.char_is_quoted_function,
completer.filename_quoting_function,
completer.filename_dequoting_function,
))

completer = Completer()


class Completion(object):
    """Interface to the active readline completion.

    This class is not intended for instantiation beyond
    the one ``completion`` object in this module.
    """

    @property
    def begidx(self):
        """The start index of the word in the line buffer."""
        return readline.get_begidx()

    @property
    def endidx(self):
        """The end index of the word in the line buffer."""
        return readline.get_endidx()

    @property
    def completion_type(self):
        """The type of completion readline performs."""
        return readline.get_completion_type()

    @property
    def invoking_key(self):
        """The last character in the key sequence that invoked completion."""
        return readline.get_completion_invoking_key()

    @property
    def found_quote(self):
        """True if the word contains or is delimited by a quote character."""
        return readline.get_completion_found_quote()

    @property
    def quote_character(self):
        """Set to the quote character found."""
        return readline.get_completion_quote_character()

    @property
    def rl_point(self):
        """The position of the cursor in the line."""
        return readline.get_rl_point()

    @property
    def rl_end(self):
        """The last position in the line."""
        return readline.get_rl_end()

    @apply
    def line_buffer():
        doc="""The line being edited."""
        def get(self):
            return readline.get_line_buffer()
        def set(self, string):
            readline.replace_line(string)
        return property(get, set, doc=doc)

    @apply
    def append_character():
        doc="""The character appended when the completion returns a
        single match. Defaults to ' '."""
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            readline.set_completion_append_character(string)
        return property(get, set, doc=doc)

    @apply
    def suppress_append():
        doc="""Suppress the append character for this completion."""
        def get(self):
            return readline.get_completion_suppress_append()
        def set(self, bool):
            readline.set_completion_suppress_append(bool)
        return property(get, set, doc=doc)

    @apply
    def suppress_quote():
        doc="""Do not append a matching quote character when performing
        completion on a quoted string."""
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, bool):
            readline.set_completion_suppress_quote(bool)
        return property(get, set, doc=doc)

    @apply
    def attempted_completion_over():
        doc="""Do not fall back to the default (filename) completion,
        even if the current completion returns no matches."""
        def get(self):
            return readline.get_attempted_completion_over()
        def set(self, bool):
            readline.set_attempted_completion_over(bool)
        return property(get, set, doc=doc)

    @apply
    def filename_completion_desired():
        doc="""Treat the results of matches as filenames.
        Directories will have a slash appended, for example."""
        def get(self):
            return readline.get_filename_completion_desired()
        def set(self, bool):
            readline.set_filename_completion_desired(bool)
        return property(get, set, doc=doc)

    @apply
    def filename_quoting_desired():
        doc="""Quote completed words according to the rules for filename
        quoting."""
        def get(self):
            return readline.get_filename_quoting_desired()
        def set(self, bool):
            readline.set_filename_quoting_desired(bool)
        return property(get, set, doc=doc)

    @apply
    def inhibit_completion():
        doc="""Insert the completion character like any other character."""
        def get(self):
            return readline.get_inhibit_completion()
        def set(self, bool):
            readline.set_inhibit_completion(bool)
        return property(get, set, doc=doc)

    # Completion functions

    def complete_filename(self, text):
        """Built-in filename completion."""
        return self._generate(text, readline.filename_completion_function)

    def complete_username(self, text):
        """Built-in username completion."""
        return self._generate(text, readline.username_completion_function)

    def expand_tilde(self, text):
        """Built-in tilde expansion."""
        return readline.tilde_expand(text)

    def display_match_list(self, substitution, matches, longest_match_length):
        """Built-in matches display."""
        readline.display_match_list(substitution, matches, longest_match_length)

    def _generate(self, text, entry_func):
        new = []
        for i in range(_MAXMATCHES):
            n = entry_func(text, i)
            if n is not None:
                new.append(n)
            else:
                break
        return new

    # Debugging

    def _dump(self, stream=sys.stdout):
        stream.write("""\
line_buffer:                    %r
begidx:                         %s
endidx:                         %s
completion_type:                %s (%r)
invoking_key:                   %r
append_character:               %r
suppress_append:                %s
found_quote:                    %s
quote_character:                %r
suppress_quote:                 %s
attempted_completion_over:      %s
filename_completion_desired:    %s
filename_quoting_desired:       %s
sort_matches:                   %s
ignore_duplicates:              %s
mark_symlink_dirs:              %s
inhibit_completion:             %s
""" % (
completion.line_buffer,
completion.begidx,
completion.endidx,
completion.completion_type, chr(completion.completion_type),
completion.invoking_key,
completion.append_character,
completion.suppress_append,
completion.found_quote,
completion.quote_character,
completion.suppress_quote,
completion.attempted_completion_over,
completion.filename_completion_desired,
completion.filename_quoting_desired,
completion.sort_matches,
completion.ignore_duplicates,
completion.mark_symlink_dirs,
completion.inhibit_completion,
))

completion = Completion()


class _GeneratorFunction(object):
    """Generator function implementation."""

    def __init__(self, compfunc):
        """Initialize the generator."""
        self.compfunc = compfunc

    def __call__(self, text, state):
        """Implement the generator protocol.

        Calls ``compfunc`` once, passing ``text`` as the only argument.
        Returns the resulting matches according to readline's generator
        protocol.
        """
        if state == 0:
            self.matches = self.compfunc(text)
            if not isinstance(self.matches, list):
                self.matches = list(self.matches)
        try:
            return self.matches[state]
        except IndexError:
            return None


def generator(compfunc):
    """Generator function factory.

    Takes a callable returning a list of matches and returns an
    object implementing the generator protocol readline requires.
    """
    return _GeneratorFunction(compfunc)


def print_exc(func):
    """Decorator printing exceptions to stderr.

    Useful when debugging completions and hooks, as exceptions occurring
    there are usually swallowed by the in-between C code.
    """

    def wrapped_func(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            import traceback; traceback.print_exc()
            raise

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func


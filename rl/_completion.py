"""Interface to the readline completer."""

import sys
import _readline as readline


def apply(func):
    """Python3 has no ``apply``."""
    return func()


class Completer(object):
    """Interface to the readline completer.

    This class is not intended for instantiation beyond
    the one ``completer`` object in this module.
    Applications wanting to use the Completer interface will
    typically import the ``completer`` object and use its
    properties and methods to configure readline.

    Example::

        from rl import completer

        completer.quote_characters = '"\\''
        completer.query_items = 100
        completer.parse_and_bind('tab: complete')
    """

    __slots__ = ()

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
        doc="""Characters that trigger filename quoting."""
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            readline.set_filename_quote_characters(string)
        return property(get, set, doc=doc)

    @apply
    def match_hidden_files():
        doc="""If True, include hidden files when matching filenames.
        Defaults to True."""
        def get(self):
            return readline.get_match_hidden_files()
        def set(self, bool):
            readline.set_match_hidden_files(bool)
        return property(get, set, doc=doc)

    @apply
    def tilde_expansion():
        doc="""If True, completion functions perform tilde expansion.
        Defaults to False."""
        def get(self):
            return readline.get_complete_with_tilde_expansion()
        def set(self, bool):
            readline.set_complete_with_tilde_expansion(bool)
        return property(get, set, doc=doc)

    @apply
    def inhibit_completion():
        doc="""If True, completion is disabled. Defaults to False."""
        def get(self):
            return readline.get_inhibit_completion()
        def set(self, bool):
            readline.set_inhibit_completion(bool)
        return property(get, set, doc=doc)

    @apply
    def query_items():
        doc="""Threshold above which the user is prompted if he
        really wants to see all matches. Defaults to 100. A negative value
        means never prompt. The prompt is bypassed if a custom
        ``display_matches_hook`` is installed."""
        def get(self):
            return readline.get_completion_query_items()
        def set(self, int):
            readline.set_completion_query_items(int)
        return property(get, set, doc=doc)

    @apply
    def completer():
        doc="""The completion entry function.
        The function is called as ``function(text, state)`` for state
        in 0, 1, 2, ... until it returns None. It should return the
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
        break characters for the current completion, or None
        to indicate no change. The passed-in ``begidx`` and ``endidx``
        are what readline would use if the hook did not exist (and
        will use if the hook returns None)."""
        def get(self):
            return readline.get_completion_word_break_hook()
        def set(self, function):
            readline.set_completion_word_break_hook(function)
        return property(get, set, doc=doc)

    @apply
    def directory_completion_hook():
        doc="""The directory completion hook function.
        This hook is used to prepare the directory name passed
        to ``opendir`` during filename completion.
        The function is called as ``function(dirname)`` and should
        return a new directory name or None to indicate no change.
        At the least, the function must perform all necessary
        dequoting."""
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
        The function is called as ``function(text, single_match, quote_char)``
        and should return a string representing a quoted version
        of ``text``, or None to indicate no change. The ``single_match``
        argument is True if the completion has generated only one match
        (may be used to close quotes)."""
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

    @apply
    def ignore_some_completions_function():
        doc="""The filename filter function.
        The function is called as ``function(substitution, matches)``
        after all filenames have been generated and should return a
        filtered subset of ``matches``, or None to indicate no change."""
        def get(self):
            return readline.get_ignore_some_completions_function()
        def set(self, function):
            readline.set_ignore_some_completions_function(function)
        return property(get, set, doc=doc)

    # Configuration functions

    def read_init_file(self, filename):
        """Parse a readline initialization file."""
        return readline.read_init_file(filename)

    def parse_and_bind(self, line):
        """Parse one line of a readline initialization file."""
        return readline.parse_and_bind(line)

    # Debugging

    def dump(self, stream=sys.stdout):
        """Dump properties to stream."""
        stream.write("""\
quote_characters:                 %r
word_break_characters:            %r
special_prefixes:                 %r
filename_quote_characters:        %r
match_hidden_files:               %s
tilde_expansion:                  %s
query_items:                      %d
inhibit_completion:               %s
completer:                        %r
startup_hook:                     %r
pre_input_hook:                   %r
word_break_hook:                  %r
directory_completion_hook:        %r
display_matches_hook:             %r
char_is_quoted_function:          %r
filename_quoting_function:        %r
filename_dequoting_function:      %r
ignore_some_completions_function: %r
""" % (
self.quote_characters,
self.word_break_characters,
self.special_prefixes,
self.filename_quote_characters,
self.match_hidden_files,
self.tilde_expansion,
self.query_items,
self.inhibit_completion,
self.completer,
self.startup_hook,
self.pre_input_hook,
self.word_break_hook,
self.directory_completion_hook,
self.display_matches_hook,
self.char_is_quoted_function,
self.filename_quoting_function,
self.filename_dequoting_function,
self.ignore_some_completions_function,
))

completer = Completer()


class Completion(object):
    """Interface to the active readline completion.

    This class is not intended for instantiation beyond
    the one ``completion`` object in this module.
    Applications wanting to use the Completion interface will
    typically import the ``completion`` object and use its
    properties and methods to implement custom completions.

    Example::

        from rl import completion

        def complete(text):
            completion.append_character = '@'
            return completion.complete_username(text)
    """

    __slots__ = ()

    @property
    def begidx(self):
        """The start index of the word in the line."""
        return readline.get_begidx()

    @property
    def endidx(self):
        """The end index of the word in the line."""
        return readline.get_endidx()

    @apply
    def line_buffer():
        doc="""The line buffer readline uses. This property
        may be assigned to to change the contents of the line."""
        def get(self):
            return readline.get_line_buffer()
        def set(self, string):
            readline.replace_line(string)
        return property(get, set, doc=doc)

    @property
    def completion_type(self):
        """The type of completion readline performs."""
        return readline.get_completion_type()

    @apply
    def append_character():
        doc="""The character appended when the completion returns a
        single match. Defaults to the space character."""
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            readline.set_completion_append_character(string)
        return property(get, set, doc=doc)

    @apply
    def suppress_append():
        doc="""Suppress the append character for this completion.
        Defaults to False."""
        def get(self):
            return readline.get_completion_suppress_append()
        def set(self, bool):
            readline.set_completion_suppress_append(bool)
        return property(get, set, doc=doc)

    @property
    def quote_character(self):
        """The quote character found (if any)."""
        return readline.get_completion_quote_character()

    @apply
    def suppress_quote():
        doc="""Do not append a matching quote character when completing
        a quoted string. Defaults to False."""
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, bool):
            readline.set_completion_suppress_quote(bool)
        return property(get, set, doc=doc)

    @property
    def found_quote(self):
        """True if the word contains or is delimited by any quote
        character, including backslashes."""
        return readline.get_completion_found_quote()

    @apply
    def filename_completion_desired():
        doc="""Treat the results of matches as filenames.
        Directory names will have a slash appended, for example.
        Defaults to False."""
        def get(self):
            return readline.get_filename_completion_desired()
        def set(self, bool):
            readline.set_filename_completion_desired(bool)
        return property(get, set, doc=doc)

    @apply
    def filename_quoting_desired():
        doc="""If results are filenames, quote them. Defaults to True.
        Has no effect if ``filename_completion_desired`` is False."""
        def get(self):
            return readline.get_filename_quoting_desired()
        def set(self, bool):
            readline.set_filename_quoting_desired(bool)
        return property(get, set, doc=doc)

    @property
    def rl_point(self):
        """The position of the cursor in the line."""
        return readline.get_rl_point()

    @property
    def rl_end(self):
        """The last position in the line. The cursor range
        is defined as: ``0 <= rl_point <= rl_end``."""
        return readline.get_rl_end()

    # Built-in functions

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

    def read_key(self):
        """Read a key from readline's input stream (the keyboard)."""
        return readline.read_key()

    def redisplay(self, force=False):
        """Refresh what's displayed on the screen."""
        readline.redisplay(force)

    def _generate(self, text, entry_func):
        """Extract a list of matches from a generator function."""
        matches = []
        i = 0
        while True:
            n = entry_func(text, i)
            if n is not None:
                matches.append(n)
                i += 1
            else:
                return matches

    # Debugging

    def dump(self, stream=sys.stdout):
        """Dump properties to stream."""
        stream.write("""\
line_buffer:                      %r
begidx:                           %d
endidx:                           %d
completion_type:                  %r
append_character:                 %r
suppress_append:                  %s
found_quote:                      %s
quote_character:                  %r
suppress_quote:                   %s
filename_completion_desired:      %s
filename_quoting_desired:         %s
""" % (
self.line_buffer,
self.begidx,
self.endidx,
self.completion_type,
self.append_character,
self.suppress_append,
self.found_quote,
self.quote_character,
self.suppress_quote,
self.filename_completion_desired,
self.filename_quoting_desired,
))

completion = Completion()


def generator(func):
    """Generator function factory.

    Takes a function returning a list of matches and returns an
    object implementing the generator protocol readline requires.
    The function is called as ``func(text)`` and should return an
    iterable of matches for ``text``.
    """
    d = {}

    def generator_func(*args):
        # We are called as func(text, state) or func(self, text, state)
        # depending on whether we wrap a function or instance method.
        state, args = args[-1], args[:-1]
        if state == 0:
            d['matches'] = func(*args)
            if not isinstance(d['matches'], list):
                d['matches'] = list(d['matches'])
        try:
            return d['matches'][state]
        except (KeyError, IndexError):
            return None

    # Allow to wrap callable non-functions which may not have a __name__
    generator_func.__name__ = getattr(func, '__name__', func.__class__.__name__)
    generator_func.__dict__ = func.__dict__
    generator_func.__doc__ = func.__doc__
    return generator_func


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


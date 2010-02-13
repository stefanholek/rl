"""Readline completion support."""

from rl import readline
from rl.utils import apply


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
        doc="""Characters that must be quoted when they appear in filenames."""
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            readline.set_filename_quote_characters(string)
        return property(get, set, doc=doc)

    @apply
    def inhibit_completion():
        doc="""If True, completion is disabled and the completion character
        is inserted as any other character. Defaults to False."""
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

    @apply
    def line_buffer():
        doc="""The line buffer readline uses. The property
        may be assigned to to change the contents of the line."""
        def get(self):
            return readline.get_line_buffer()
        def set(self, string):
            readline.replace_line(string)
        return property(get, set, doc=doc)

    @apply
    def completion_type():
        doc="""The type of completion readline performs."""
        def get(self):
            return readline.get_completion_type()
        def set(self, string):
            readline.set_completion_type(string)
        return property(get, set, doc=doc)

    @apply
    def begidx():
        doc="""The start index of the word in the line."""
        def get(self):
            return readline.get_begidx()
        def set(self, int):
            readline.set_begidx(int)
        return property(get, set, doc=doc)

    @apply
    def endidx():
        doc="""The end index of the word in the line."""
        def get(self):
            return readline.get_endidx()
        def set(self, int):
            readline.set_endidx(int)
        return property(get, set, doc=doc)

    @apply
    def found_quote():
        doc="""True if the word contains or is delimited by any quote
        character, including backslashes."""
        def get(self):
            return readline.get_completion_found_quote()
        def set(self, bool):
            readline.set_completion_found_quote(bool)
        return property(get, set, doc=doc)

    @apply
    def quote_character():
        doc="""The quote character found (not including backslashes)."""
        def get(self):
            return readline.get_completion_quote_character()
        def set(self, string):
            readline.set_completion_quote_character(string)
        return property(get, set, doc=doc)

    @apply
    def suppress_quote():
        doc="""Do not append a matching quote character when completing
        a quoted string. Defaults to False."""
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, bool):
            readline.set_completion_suppress_quote(bool)
        return property(get, set, doc=doc)

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
            d['matches'] = iter(func(*args))
        try:
            return d['matches'].next()
        except StopIteration:
            return None

    # Allow to wrap callable non-functions which may not have a __name__
    generator_func.__name__ = getattr(func, '__name__', func.__class__.__name__)
    generator_func.__module__ = func.__module__
    generator_func.__doc__ = func.__doc__
    generator_func.__dict__.update(func.__dict__)
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
    wrapped_func.__module__ = func.__module__
    wrapped_func.__doc__ = func.__doc__
    wrapped_func.__dict__.update(func.__dict__)
    return wrapped_func


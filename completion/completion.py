# Alternative readline interface focusing on completion

import sys
import readline

# Rein in runaway completions
_MAXMATCHES = 100000


def print_exc(func):
    """Decorator printing exceptions to stderr.

    Useful for debugging completions and hooks.
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


class Completer(object):
    """Interface to the readline completer."""

    # For filename_quoting_function
    SINGLE_MATCH = 1
    MULT_MATCH = 2

    @property
    def basic_quote_characters(self):
        return readline.get_basic_quote_characters()

    @property
    def basic_word_break_characters(self):
        return readline.get_basic_word_break_characters()

    @apply
    def quote_characters():
        def get(self):
            return readline.get_completer_quote_characters()
        def set(self, string):
            readline.set_completer_quote_characters(string)
        return property(get, set)

    @apply
    def word_break_characters():
        def get(self):
            return readline.get_completer_delims()
        def set(self, string):
            readline.set_completer_delims(string)
        return property(get, set)

    @apply
    def special_prefixes():
        def get(self):
            return readline.get_special_prefixes()
        def set(self, string):
            readline.set_special_prefixes(string)
        return property(get, set)

    @apply
    def filename_quote_characters():
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            readline.set_filename_quote_characters(string)
        return property(get, set)

    @apply
    def match_hidden_files():
        def get(self):
            return readline.get_match_hidden_files()
        def set(self, value):
            readline.set_match_hidden_files(value)
        return property(get, set)

    @apply
    def tilde_expansion():
        def get(self):
            return readline.get_complete_with_tilde_expansion()
        def set(self, value):
            readline.set_complete_with_tilde_expansion(value)
        return property(get, set)

    @apply
    def query_items():
        def get(self):
            return readline.get_completion_query_items()
        def set(self, value):
            readline.set_completion_query_items(value)
        return property(get, set)

    @apply
    def completer():
        def get(self):
            return readline.get_completer()
        def set(self, function):
            readline.set_completer(function)
        return property(get, set)

    @apply
    def startup_hook():
        def get(self):
            return readline.get_startup_hook()
        def set(self, function):
            readline.set_startup_hook(function)
        return property(get, set)

    @apply
    def pre_input_hook():
        def get(self):
            return readline.get_pre_input_hook()
        def set(self, function):
            readline.set_pre_input_hook(function)
        return property(get, set)

    @apply
    def word_break_hook():
        def get(self):
            return readline.get_completion_word_break_hook()
        def set(self, function):
            readline.set_completion_word_break_hook(function)
        return property(get, set)

    @apply
    def directory_completion_hook():
        def get(self):
            return readline.get_directory_completion_hook()
        def set(self, function):
            readline.set_directory_completion_hook(function)
        return property(get, set)

    @apply
    def display_matches_hook():
        def get(self):
            return readline.get_completion_display_matches_hook()
        def set(self, function):
            readline.set_completion_display_matches_hook(function)
        return property(get, set)

    @apply
    def char_is_quoted_function():
        def get(self):
            return readline.get_char_is_quoted_function()
        def set(self, function):
            readline.set_char_is_quoted_function(function)
        return property(get, set)

    @apply
    def filename_quoting_function():
        def get(self):
            return readline.get_filename_quoting_function()
        def set(self, function):
            readline.set_filename_quoting_function(function)
        return property(get, set)

    @apply
    def filename_dequoting_function():
        def get(self):
            return readline.get_filename_dequoting_function()
        def set(self, function):
            readline.set_filename_dequoting_function(function)
        return property(get, set)

    # Configuration

    def read_init_file(self, filename):
        return readline.read_init_file(filename)

    def parse_and_bind(self, line):
        return readline.parse_and_bind(line)

    # Debugging

    def dump_vars(self):
        sys.stdout.write("""\
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
    """Interface to the active readline completion."""

    @property
    def begidx(self):
        return readline.get_begidx()

    @property
    def endidx(self):
        return readline.get_endidx()

    @property
    def completion_type(self):
        return readline.get_completion_type()

    @property
    def invoking_key(self):
        return readline.get_completion_invoking_key()

    @property
    def found_quote(self):
        return readline.get_completion_found_quote()

    @property
    def quote_character(self):
        return readline.get_completion_quote_character()

    @property
    def rl_point(self):
        return readline.get_rl_point()

    @property
    def rl_end(self):
        return readline.get_rl_end()

    @apply
    def line_buffer():
        def get(self):
            return readline.get_line_buffer()
        def set(self, string):
            readline.replace_line(string)
        return property(get, set)

    @apply
    def append_character():
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            readline.set_completion_append_character(string)
        return property(get, set)

    @apply
    def suppress_append():
        def get(self):
            return readline.get_completion_suppress_append()
        def set(self, value):
            readline.set_completion_suppress_append(value)
        return property(get, set)

    @apply
    def suppress_quote():
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, value):
            readline.set_completion_suppress_quote(value)
        return property(get, set)

    @apply
    def attempted_completion_over():
        def get(self):
            return readline.get_attempted_completion_over()
        def set(self, value):
            readline.set_attempted_completion_over(value)
        return property(get, set)

    @apply
    def filename_completion_desired():
        def get(self):
            return readline.get_filename_completion_desired()
        def set(self, value):
            readline.set_filename_completion_desired(value)
        return property(get, set)

    @apply
    def filename_quoting_desired():
        def get(self):
            return readline.get_filename_quoting_desired()
        def set(self, value):
            readline.set_filename_quoting_desired(value)
        return property(get, set)

    @apply
    def sort_matches():
        def get(self):
            return readline.get_sort_completion_matches()
        def set(self, value):
            readline.set_sort_completion_matches(value)
        return property(get, set)

    @apply
    def ignore_duplicates():
        def get(self):
            return readline.get_ignore_completion_duplicates()
        def set(self, value):
            readline.set_ignore_completion_duplicates(value)
        return property(get, set)

    @apply
    def mark_symlink_dirs():
        def get(self):
            return readline.get_completion_mark_symlink_dirs()
        def set(self, value):
            readline.set_completion_mark_symlink_dirs(value)
        return property(get, set)

    @apply
    def inhibit_completion():
        def get(self):
            return readline.get_inhibit_completion()
        def set(self, value):
            readline.set_inhibit_completion(value)
        return property(get, set)

    # Stock completions

    def filename_completion_function(self, text):
        return self.__matches(text, readline.filename_completion_function)

    def username_completion_function(self, text):
        return self.__matches(text, readline.username_completion_function)

    def tilde_expand(self, text):
        return readline.tilde_expand(text)

    def __matches(self, text, entry_func):
        new = []
        for i in range(_MAXMATCHES):
            n = entry_func(text, i)
            if n is not None:
                new.append(n)
            else:
                break
        return new

    # Input stream interaction

    def read_key(self):
        return readline.read_key()

    def stuff_char(self, char):
        return readline.stuff_char(char)

    # Display

    def display_match_list(self, substitution, matches, max_length):
        readline.display_match_list(substitution, matches, max_length)

    def redisplay(self, force=False):
        readline.redisplay(force)

    # Debugging

    def dump_vars(self):
        sys.stdout.write("""\
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


class generator(object):
    """Turn any callable returning a list of matches into a
    completion_entry_function that can be handed to readline.
    """

    def __init__(self, func):
        self._func = func

    def __call__(self, text, state):
        if state == 0:
            self._matches = self._func(text)
        try:
            return self._matches[state]
        except IndexError:
            return None


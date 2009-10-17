"""Test helpers."""

from rl import completer
from rl import completion

PYTHON_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


def reset_completer():
    completer.quote_characters = ''
    completer.word_break_characters = PYTHON_DELIMS
    completer.special_prefixes = ''
    completer.filename_quote_characters = ''
    completer.match_hidden_files = True
    completer.tilde_expansion = False
    completer.inhibit_completion = False
    completer.query_items = 100
    completer.completer = None
    completer.startup_hook = None
    completer.pre_input_hook = None
    completer.word_break_hook = None
    completer.directory_completion_hook = None
    completer.display_matches_hook = None
    completer.char_is_quoted_function = None
    completer.filename_quoting_function = None
    completer.filename_dequoting_function = None
    completer.ignore_some_completions_function = None


def reset_completion():
    completion.line_buffer = ''
    completion.append_character = ' '
    completion.suppress_append = False
    completion.suppress_quote = False
    completion.filename_completion_desired = False
    completion.filename_quoting_desired = True


def reset():
    reset_completer()
    reset_completion()


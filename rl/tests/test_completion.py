import unittest
import StringIO

from rl import completer
from rl import completion

PYTHON_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


def hook(*args, **kw):
    pass


class CompleterTests(unittest.TestCase):

    def test_quote_characters(self):
        self.assertEqual(completer.quote_characters, '')
        completer.quote_characters = '"\''
        self.assertEqual(completer.quote_characters, '"\'')
        completer.quote_characters = ''
        self.assertEqual(completer.quote_characters, '')

    def test_word_break_characters(self):
        self.assertEqual(completer.word_break_characters, PYTHON_DELIMS)
        completer.word_break_characters = ' \t\n"\'<>=;&|'
        self.assertEqual(completer.word_break_characters, ' \t\n"\'<>=;&|')
        completer.word_break_characters = ''
        self.assertEqual(completer.word_break_characters, '')

    def test_special_prefixes(self):
        self.assertEqual(completer.special_prefixes, '')
        completer.special_prefixes = '@$'
        self.assertEqual(completer.special_prefixes, '@$')
        completer.special_prefixes = ''
        self.assertEqual(completer.special_prefixes, '')

    def test_filename_quote_characters(self):
        self.assertEqual(completer.filename_quote_characters, '')
        completer.filename_quote_characters = ' \t\n\\"\''
        self.assertEqual(completer.filename_quote_characters, ' \t\n\\"\'')
        completer.filename_quote_characters = ''
        self.assertEqual(completer.filename_quote_characters, '')

    def test_match_hidden_files(self):
        self.assertEqual(completer.match_hidden_files, True)
        completer.match_hidden_files = False
        self.assertEqual(completer.match_hidden_files, False)
        completer.match_hidden_files = True
        self.assertEqual(completer.match_hidden_files, True)

    def test_tilde_expansion(self):
        self.assertEqual(completer.tilde_expansion, False)
        completer.tilde_expansion = True
        self.assertEqual(completer.tilde_expansion, True)
        completer.tilde_expansion = False
        self.assertEqual(completer.tilde_expansion, False)

    def test_inhibit_completion(self):
        self.assertEqual(completer.inhibit_completion, False)
        completer.inhibit_completion = True
        self.assertEqual(completer.inhibit_completion, True)
        completer.inhibit_completion = False
        self.assertEqual(completer.inhibit_completion, False)

    def test_query_items(self):
        self.assertEqual(completer.query_items, 100)
        completer.query_items = 200
        self.assertEqual(completer.query_items, 200)
        completer.query_items = -1
        self.assertEqual(completer.query_items, -1)

    def test_completer(self):
        self.assertEqual(completer.completer, None)
        completer.completer = hook
        self.assertEqual(completer.completer, hook)
        completer.completer = None
        self.assertEqual(completer.completer, None)

    def test_startup_hook(self):
        self.assertEqual(completer.startup_hook, None)
        completer.startup_hook = hook
        self.assertEqual(completer.startup_hook, hook)
        completer.startup_hook = None
        self.assertEqual(completer.startup_hook, None)

    def test_pre_input_hook(self):
        self.assertEqual(completer.pre_input_hook, None)
        completer.pre_input_hook = hook
        self.assertEqual(completer.pre_input_hook, hook)
        completer.pre_input_hook = None
        self.assertEqual(completer.pre_input_hook, None)

    def test_word_break_hook(self):
        self.assertEqual(completer.word_break_hook, None)
        completer.word_break_hook = hook
        self.assertEqual(completer.word_break_hook, hook)
        completer.word_break_hook = None
        self.assertEqual(completer.word_break_hook, None)

    def test_directory_completion_hook(self):
        self.assertEqual(completer.directory_completion_hook, None)
        completer.directory_completion_hook = hook
        self.assertEqual(completer.directory_completion_hook, hook)
        completer.directory_completion_hook = None
        self.assertEqual(completer.directory_completion_hook, None)

    def test_display_matches_hook(self):
        self.assertEqual(completer.display_matches_hook, None)
        completer.display_matches_hook = hook
        self.assertEqual(completer.display_matches_hook, hook)
        completer.display_matches_hook = None
        self.assertEqual(completer.display_matches_hook, None)

    def test_char_is_quoted_function(self):
        self.assertEqual(completer.char_is_quoted_function, None)
        completer.char_is_quoted_function = hook
        self.assertEqual(completer.char_is_quoted_function, hook)
        completer.char_is_quoted_function = None
        self.assertEqual(completer.char_is_quoted_function, None)

    def test_filename_quoting_function(self):
        self.assertEqual(completer.filename_quoting_function, None)
        completer.filename_quoting_function = hook
        self.assertEqual(completer.filename_quoting_function, hook)
        completer.filename_quoting_function = None
        self.assertEqual(completer.filename_quoting_function, None)

    def test_filename_dequoting_function(self):
        self.assertEqual(completer.filename_dequoting_function, None)
        completer.filename_dequoting_function = hook
        self.assertEqual(completer.filename_dequoting_function, hook)
        completer.filename_dequoting_function = None
        self.assertEqual(completer.filename_dequoting_function, None)

    def test_ignore_some_completions_function(self):
        self.assertEqual(completer.ignore_some_completions_function, None)
        completer.ignore_some_completions_function = hook
        self.assertEqual(completer.ignore_some_completions_function, hook)
        completer.ignore_some_completions_function = None
        self.assertEqual(completer.ignore_some_completions_function, None)

    def test_dump_completer(self):
        stream = StringIO.StringIO()
        completer.dump(stream)


class CompletionTests(unittest.TestCase):

    def test_dump_completion(self):
        stream = StringIO.StringIO()
        completion.dump(stream)


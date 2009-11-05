import unittest

from rl import completer
from rl import completion

from rl.testing import DEFAULT_DELIMS
from rl.testing import reset


def hook(*args):
    pass


class CompleterTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_quote_characters(self):
        self.assertEqual(completer.quote_characters, '')
        completer.quote_characters = '"\''
        self.assertEqual(completer.quote_characters, '"\'')
        completer.quote_characters = ''
        self.assertEqual(completer.quote_characters, '')

    def test_word_break_characters(self):
        self.assertEqual(completer.word_break_characters, DEFAULT_DELIMS)
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

    def test_slots(self):
        self.assertRaises(AttributeError, setattr, completer, 'foo', 1)


class CompletionTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_begidx(self):
        self.assertEqual(completion.begidx, 0)
        completion.begidx = 5
        self.assertEqual(completion.begidx, 5)
        completion.begidx = 0
        self.assertEqual(completion.begidx, 0)

    def test_endidx(self):
        self.assertEqual(completion.endidx, 0)
        completion.endidx = 5
        self.assertEqual(completion.endidx, 5)
        completion.endidx = 0
        self.assertEqual(completion.endidx, 0)

    def test_line_buffer(self):
        self.assertEqual(completion.line_buffer, '')
        completion.line_buffer = 'foo'
        self.assertEqual(completion.line_buffer, 'foo')
        completion.line_buffer = ''
        self.assertEqual(completion.line_buffer, '')

    def test_completion_type(self):
        self.assertEqual(completion.completion_type, '')
        completion.completion_type = '?'
        self.assertEqual(completion.completion_type, '?')
        completion.completion_type = ''
        self.assertEqual(completion.completion_type, '')

    def test_append_character(self):
        self.assertEqual(completion.append_character, ' ')
        completion.append_character = '$'
        self.assertEqual(completion.append_character, '$')
        completion.append_character = ''
        self.assertEqual(completion.append_character, '')

    def test_suppress_append(self):
        self.assertEqual(completion.suppress_append, False)
        completion.suppress_append = True
        self.assertEqual(completion.suppress_append, True)
        completion.suppress_append = False
        self.assertEqual(completion.suppress_append, False)

    def test_quote_character(self):
        self.assertEqual(completion.quote_character, '')
        completion.quote_character = '"'
        self.assertEqual(completion.quote_character, '"')
        completion.quote_character = ''
        self.assertEqual(completion.quote_character, '')

    def test_suppress_quote(self):
        self.assertEqual(completion.suppress_quote, False)
        completion.suppress_quote = True
        self.assertEqual(completion.suppress_quote, True)
        completion.suppress_quote = False
        self.assertEqual(completion.suppress_quote, False)

    def test_found_quote(self):
        self.assertEqual(completion.found_quote, False)
        completion.found_quote = True
        self.assertEqual(completion.found_quote, True)
        completion.found_quote = False
        self.assertEqual(completion.found_quote, False)

    def test_filename_completion_desired(self):
        self.assertEqual(completion.filename_completion_desired, False)
        completion.filename_completion_desired = True
        self.assertEqual(completion.filename_completion_desired, True)
        completion.filename_completion_desired = False
        self.assertEqual(completion.filename_completion_desired, False)

    def test_filename_quoting_desired(self):
        self.assertEqual(completion.filename_quoting_desired, True)
        completion.filename_quoting_desired = False
        self.assertEqual(completion.filename_quoting_desired, False)
        completion.filename_quoting_desired = True
        self.assertEqual(completion.filename_quoting_desired, True)

    def test_rl_point(self):
        self.assertEqual(completion.rl_point, 0)
        completion.line_buffer = 'foo'
        self.assertEqual(completion.rl_point, 3)

    def test_rl_end(self):
        self.assertEqual(completion.rl_end, 0)
        completion.line_buffer = 'foo'
        self.assertEqual(completion.rl_end, 3)

    def test_slots(self):
        self.assertRaises(AttributeError, setattr, completion, 'foo', 1)


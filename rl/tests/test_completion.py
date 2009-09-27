import unittest
import StringIO

from rl import completer
from rl import completion

PYTHON_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


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

    def test_dump_completer(self):
        stream = StringIO.StringIO()
        completer.dump(stream)


class CompletionTests(unittest.TestCase):

    def test_dump_completion(self):
        stream = StringIO.StringIO()
        completion.dump(stream)


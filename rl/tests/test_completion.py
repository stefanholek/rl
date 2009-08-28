import unittest

from completion import completer
from completion import completion


class CompletionTests(unittest.TestCase):

    def test_quote_characters(self):
        self.assertEqual(completer.quote_characters, '')
        completer.quote_characters = '"\''
        self.assertEqual(completer.quote_characters, '"\'')
        completer.quote_characters = ''
        self.assertEqual(completer.quote_characters, '')

    def test_word_break_characters(self):
        self.assertEqual(completer.word_break_characters,
                         ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?')

        completer.word_break_characters = ' \t\n\\"\'`<>=;&|?*!'
        self.assertEqual(completer.word_break_characters, ' \t\n\\"\'`<>=;&|?*!')
        completer.word_break_characters = ''
        self.assertEqual(completer.word_break_characters, '')


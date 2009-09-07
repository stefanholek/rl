import unittest
import StringIO

from rl.completion import completer
from rl.completion import completion


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

    def test_dump_completer(self):
        stream = StringIO.StringIO()
        completer._dump(stream)

    def test_dump_completion(self):
        stream = StringIO.StringIO()
        completion._dump(stream)


import unittest

from rl import completer
from rl import completion
from rl import generator
from rl import readline

from rl.testing import JailSetup
from rl.testing import reset

TAB = '\t'


called = []

def hook(*args):
    called.append(args)


@generator
def filecomplete(text):
    return completion.complete_filename(text)


class WordBreakTests(unittest.TestCase):

    def setUp(self):
        reset()
        called[:] = []

    def test_word_break_hook(self):
        completer.word_break_hook = hook
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [(0, 2)])

    def test_char_is_quoted_function(self):
        completer.char_is_quoted_function = hook
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr\\', 2), ('fr\\', 2)]) # Called twice


class CompletionMatchesTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []

    def test_completer(self):
        completer.completer = hook
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr', 0)])

    def test_directory_completion_hook(self):
        completer.completer = filecomplete
        completer.directory_completion_hook = hook
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.',)])

    def test_filename_dequoting_function(self):
        completer.completer = filecomplete
        completer.filename_dequoting_function = hook
        completion.line_buffer = 'fr\\'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.', '')])

    def test_ignore_some_completions_function(self):
        completer.completer = filecomplete
        completer.ignore_some_completions_function = hook
        self.mkfile('fred.txt')
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fred.txt', [])])

    def test_filename_quoting_function(self):
        completer.completer = filecomplete
        completer.filename_quoting_function = hook
        completer.filename_quote_characters = ' \t\n"\''
        self.mkfile('fred flintstone.txt')
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fred flintstone.txt', True, '')])


class DisplayMatchesTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []

    # XXX: Doesn't work in Python 2.5
    def test_display_matches_hook(self):
        completer.completer = filecomplete
        completer.display_matches_hook = hook
        self.mkfile('fred.txt', 'fred.gif')
        readline.complete_internal('?')
        self.assertEqual(called, [('fred.', ['fred.gif', 'fred.txt'], 8)])


class WordBreakHookTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_nohook(self):
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_nonehook(self):
        def func(begidx, endidx):
            return None
        completer.word_break_hook = func
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_badhook(self):
        def func(begidx, endidx):
            return 23
        completer.word_break_hook = func
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_replaces_word_break_characters(self):
        def func(begidx, endidx):
            return '!'
        completer.word_break_hook = func
        completer.word_break_characters = ' '
        completion.line_buffer = 'f!r ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 2)
        self.assertEqual(completion.endidx, 6)


class CharIsQuotedFunctionTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_nohook(self):
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_nonehook(self):
        def func(text, index):
            return None
        completer.char_is_quoted_function = func
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_badhook(self):
        def func(text, index):
            raise RuntimeError()
        completer.char_is_quoted_function = func
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_char_is_not_quoted(self):
        def func(text, index):
            return False
        completer.char_is_quoted_function = func
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_char_is_quoted(self):
        def func(text, index):
            return True
        completer.char_is_quoted_function = func
        completer.quote_characters = '"\''
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 0)
        self.assertEqual(completion.endidx, 6)


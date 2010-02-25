import unittest

from rl import completer
from rl import completion
from rl import generator
from rl import readline
from rl import print_exc

from rl.testing import JailSetup
from rl.testing import reset

TAB = '\t'

called = []


@print_exc
def hook(*args):
    called.append(args)


@print_exc
@generator
def filecomplete(text):
    return completion.complete_filename(text)


@print_exc
def is_quoted(text, index):
    return index > 0 and text[index-1] == '\\'


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
        completer.quote_characters = '"'
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


class CompleterTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_no_completer(self):
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr')

    def test_none_completer(self):
        @generator
        def func(text):
            return None
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr')

    def test_bad_completer(self):
        @generator
        def func(text):
            raise RuntimeError()
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr')

    def test_complete(self):
        @generator
        def func(text):
            return ['fred']
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fred ')

    def test_no_matches(self):
        @generator
        def func(text):
            return []
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr')

    def test_none_matches(self):
        @generator
        def func(text):
            return [None]
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr')

    def test_empty_string(self):
        @generator
        def func(text):
            return ['']
        completer.completer = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'fr ') # XXX Single match?


class DisplayMatchesHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []

    def test_display_matches_hook(self):
        completer.completer = filecomplete
        completer.display_matches_hook = hook
        self.mkfile('fred.txt', 'fred.gif')
        readline.complete_internal('?')
        self.assertEqual(called, [('fred.', ['fred.gif', 'fred.txt'], 8)])


class WordBreakHookTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_no_hook(self):
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_none_hook(self):
        def func(begidx, endidx):
            return None
        completer.word_break_hook = func
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_bad_hook(self):
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

    def test_empty_string(self):
        def func(begidx, endidx):
            return ''
        completer.word_break_hook = func
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 0)
        self.assertEqual(completion.endidx, 5)


class CharIsQuotedFunctionTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_no_hook(self):
        completer.quote_characters = '"'
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_none_hook(self):
        def func(text, index):
            return None
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_bad_hook(self):
        def func(text, index):
            raise RuntimeError()
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)

    def test_char_is_quoted(self):
        def func(text, index):
            return True
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 0)
        self.assertEqual(completion.endidx, 6)

    def test_char_is_not_quoted(self):
        def func(text, index):
            return False
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(completion.begidx, 4)
        self.assertEqual(completion.endidx, 6)


class DirectoryCompletionHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.quote_characters = '\'"'
        completer.word_break_characters = ' \t\n"\''
        completer.filename_quote_characters = ' \t\n"\''
        completer.char_is_quoted_function = is_quoted
        completer.completer = filecomplete

    def test_no_hook(self):
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "flint\\ stone/fr")

    def test_none_hook(self):
        def func(dirname):
            return None
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "flint\\ stone/fr")

    def test_bad_hook(self):
        def func(dirname):
            return 23
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "flint\\ stone/fr")

    def test_directory_completion_hook(self):
        def func(dirname):
            called.append(dirname)
            return dirname.replace('\\', '')
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['flint\\ stone/'])
        self.assertEqual(completion.line_buffer, "'flint stone/fred.txt' ")

    def test_no_dequoting(self):
        def func(dirname):
            called.append(dirname)
            return dirname
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['flint\\ stone/'])
        self.assertEqual(completion.line_buffer, "flint\\ stone/fr")

    def test_empty_string(self):
        def func(dirname):
            return ''
        self.mkdir('flint stone')
        self.mkfile('flint stone/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'flint\\ stone/fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "flint\\ stone/fr")


class FilenameDequotingFunctionTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.quote_characters = '\'"'
        completer.word_break_characters = ' \t\n"\''
        completer.filename_quote_characters = ' \t\n"\''
        completer.char_is_quoted_function = is_quoted
        completer.completer = filecomplete

    def test_no_hook(self):
        self.mkfile('fr ed.txt')
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fr\\ ")

    def test_none_hook(self):
        def func(text, quote_char):
            return None
        self.mkfile('fr ed.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fr\\ ")

    def test_bad_hook(self):
        def func(text, quote_char):
            return 23
        self.mkfile('fr ed.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fr\\ ")

    def test_filename_dequoting_function(self):
        def func(text, quote_char):
            called.append((text, quote_char))
            return text.replace('\\', '')
        self.mkfile('fr ed.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.', ''), ('fr\\ ', '')])
        self.assertEqual(completion.line_buffer, "'fr ed.txt' ")

    def test_no_dequoting(self):
        def func(text, quote_char):
            called.append((text, quote_char))
            return text
        self.mkfile('fr ed.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.', ''), ('fr\\ ', '')])
        self.assertEqual(completion.line_buffer, "fr\\ ")

    def test_quote_char(self):
        def func(text, quote_char):
            called.append((text, quote_char))
            return text
        self.mkfile('fr ed.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = "'fr "
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.', "'"), ('fr ', "'")])
        self.assertEqual(completion.line_buffer, "'fr ed.txt' ")

    def test_empty_string(self):
        def func(text, quote_char):
            return ''
        self.mkfile('fr ed.txt')
        self.mkfile('fr ed.gif')
        completer.filename_dequoting_function = func
        completion.line_buffer = 'fr\\ '
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "'fr ed.") # XXX Match?


class IgnoreSomeCompletionsFunctionTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.completer = filecomplete

    def test_no_hook(self):
        self.mkfile('fred.txt')
        self.mkfile('fred.gif')
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fred.")

    def test_none_hook(self):
        def func(substitution, matches):
            return None
        self.mkfile('fred.txt')
        self.mkfile('fred.gif')
        completer.ignore_some_completions_function = func
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fred.")

    def test_bad_hook(self):
        def func(substitution, matches):
            return 23
        self.mkfile('fred.txt')
        self.mkfile('fred.gif')
        completer.ignore_some_completions_function = func
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fred.")

    def test_ignore_some_completions_function(self):
        def func(substitution, matches):
            called.append((substitution, matches))
            return [x for x in matches if not x.endswith('gif')]
        self.mkfile('fred.txt')
        self.mkfile('fred.gif')
        completer.ignore_some_completions_function = func
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fred.', ['fred.gif', 'fred.txt'])])
        self.assertEqual(completion.line_buffer, "fred.txt ")

    def test_no_ignore(self):
        def func(substitution, matches):
            called.append((substitution, matches))
            return matches
        self.mkfile('fred.txt')
        self.mkfile('fred.gif')
        completer.ignore_some_completions_function = func
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fred.', ['fred.gif', 'fred.txt'])])
        self.assertEqual(completion.line_buffer, "fred.")


class FilenameQuotingFunctionTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.quote_characters = '\'"'
        completer.word_break_characters = ' \t\n"\''
        completer.filename_quote_characters = ' \t\n"\''
        completer.char_is_quoted_function = is_quoted
        completer.completer = filecomplete

    def test_no_hook(self):
        self.mkfile('fr ed.txt')
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "'fr ed.txt' ") # XXX Default impl kicks in

    def test_none_hook(self):
        def func(text, single_match, quote_char):
            return None
        self.mkfile('fr ed.txt')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fr ed.txt ")

    def test_bad_hook(self):
        def func(text, single_match, quote_char):
            return 23
        self.mkfile('fr ed.txt')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, "fr ed.txt ")

    def test_filename_quoting_function(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return text.replace(' ', '\\ ')
        self.mkfile('fr ed.txt')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr ed.txt', True, '')])
        self.assertEqual(completion.line_buffer, "fr\\ ed.txt ")

    def test_no_quoting(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return text
        self.mkfile('fr ed.txt')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr ed.txt', True, '')])
        self.assertEqual(completion.line_buffer, "fr ed.txt ")

    def test_multi_match(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return text.replace(' ', '\\ ')
        self.mkfile('fr ed.txt')
        self.mkfile('fr ed.gif')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr ed.', False, '')])
        self.assertEqual(completion.line_buffer, "fr\\ ed.")

    def test_quote_char(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return quote_char + text
        self.mkfile('fr ed.txt')
        self.mkfile('fr ed.gif')
        completer.filename_quoting_function = func
        completion.line_buffer = "'fr"
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr ed.', False, "'")])
        self.assertEqual(completion.line_buffer, "'fr ed.")

    def test_empty_string(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return ''
        self.mkfile('fr ed.txt')
        self.mkfile('fr ed.gif')
        completer.filename_quoting_function = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, '')


# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

import unittest
import unicodedata
import sys

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


def decompose(text):
    # HFS Plus uses decomposed UTF-8
    if sys.platform != 'darwin':
        return text
    if sys.version_info[0] >= 3:
        return unicodedata.normalize('NFD', text)
    else:
        return unicodedata.normalize('NFD', text.decode('utf-8')).encode('utf-8')


class CompleterTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_complete_utf8(self):
        @generator
        def func(text):
            return ['Mädchen']
        completer.completer = func
        completion.line_buffer = 'Mä'
        readline.complete_internal(TAB)
        self.assertEqual(completion.line_buffer, 'Mädchen ')


class DisplayMatchesHookTests(unittest.TestCase):

    def setUp(self):
        reset()
        called[:] = []

    def test_display_matches_hook_utf8(self):
        @generator
        def func(text):
            return ['Mädchen.gif', 'Mädchen.txt']
        completer.completer = func
        completer.display_matches_hook = hook
        readline.complete_internal('?')
        self.assertEqual(called,
            [('Mädchen.', ['Mädchen.gif', 'Mädchen.txt'], 11)]) # "maximum printed length"


class WordBreakHookTests(unittest.TestCase):

    def setUp(self):
        reset()
        called[:] = []

    def test_word_break_hook_indexes(self):
        completer.word_break_hook = hook
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr ed'
        readline.complete_internal(TAB)
        self.assertEqual(called, [(3, 5)])
        self.assertEqual(completion.begidx, 3)
        self.assertEqual(completion.endidx, 5)

    def test_word_break_hook_utf8(self):
        completer.word_break_hook = hook
        completer.word_break_characters = ' '
        completion.line_buffer = 'Mä dchen'
        readline.complete_internal(TAB)
        if sys.version_info[0] >= 3:
            self.assertEqual(called, [(3, 8)])
            self.assertEqual(completion.begidx, 3)
            self.assertEqual(completion.endidx, 8)
        else:
            self.assertEqual(called, [(4, 9)])
            self.assertEqual(completion.begidx, 4)
            self.assertEqual(completion.endidx, 9)


class CharIsQuotedFunctionTests(unittest.TestCase):

    def setUp(self):
        reset()
        called[:] = []

    def test_char_is_quoted_indexes(self):
        def func(text, index):
            called.append((text, index))
            return is_quoted(text, index)
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completer.word_break_characters = ' '
        completion.line_buffer = 'fr\\ ed'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('fr\\ ed', 3),
                                  ('fr\\ ed', 0)])
        self.assertEqual(completion.begidx, 0)
        self.assertEqual(completion.endidx, 6)

    def test_char_is_quoted_utf8(self):
        def func(text, index):
            called.append((text, index))
            return is_quoted(text, index)
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completer.word_break_characters = ' '
        completion.line_buffer = 'Mä\\ dchen'
        readline.complete_internal(TAB)
        if sys.version_info[0] >= 3:
            self.assertEqual(called, [('Mä\\ dchen', 3),
                                      ('Mä\\ dchen', 0)])
            self.assertEqual(completion.begidx, 0)
            self.assertEqual(completion.endidx, 9)
        else:
            self.assertEqual(called, [('M\xc3\xa4\\ dchen', 4),
                                      ('M\xc3\xa4\\ dchen', 0)])
            self.assertEqual(completion.begidx, 0)
            self.assertEqual(completion.endidx, 10)

    def test_char_is_quoted_multi_utf8(self):
        def func(text, index):
            called.append((text, index))
            return is_quoted(text, index)
        completer.char_is_quoted_function = func
        completer.quote_characters = '"'
        completer.word_break_characters = ' '
        completion.line_buffer = 'Ää\\ ÖöÜü\\ abc'
        readline.complete_internal(TAB)
        if sys.version_info[0] >= 3:
            self.assertEqual(called, [('Ää\\ ÖöÜü\\ abc', 9),
                                      ('Ää\\ ÖöÜü\\ abc', 3),
                                      ('Ää\\ ÖöÜü\\ abc', 0)])
            self.assertEqual(completion.begidx, 0)
            self.assertEqual(completion.endidx, 13)
        else:
            self.assertEqual(called, [('\xc3\x84\xc3\xa4\\ \xc3\x96\xc3\xb6\xc3\x9c\xc3\xbc\\ abc', 15),
                                      ('\xc3\x84\xc3\xa4\\ \xc3\x96\xc3\xb6\xc3\x9c\xc3\xbc\\ abc', 5),
                                      ('\xc3\x84\xc3\xa4\\ \xc3\x96\xc3\xb6\xc3\x9c\xc3\xbc\\ abc', 0)])
            self.assertEqual(completion.begidx, 0)
            self.assertEqual(completion.endidx, 19)


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

    def test_directory_completion_hook(self):
        def func(dirname):
            called.append(dirname)
            return dirname.replace('\\', '')
        self.mkdir('Mä dchen')
        self.mkfile('Mä dchen/fred.txt')
        completer.directory_completion_hook = func
        completion.line_buffer = 'Mä\\ dchen/fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['Mä\\ dchen/'])
        self.assertEqual(completion.line_buffer, "'Mä dchen/fred.txt' ")


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

    def test_filename_dequoting_function(self):
        def func(text, quote_char):
            called.append((text, quote_char))
            return text.replace('\\', '')
        self.mkfile('Mä dchen.txt')
        completer.filename_dequoting_function = func
        completion.line_buffer = decompose('Mä\\ ')
        readline.complete_internal(TAB)
        self.assertEqual(called, [('.', ''), (decompose('Mä\\ '), '')])
        self.assertEqual(completion.line_buffer, decompose("'Mä dchen.txt' "))


class IgnoreSomeCompletionsFunctionTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.completer = filecomplete

    def test_ignore_some_completions_function(self):
        def func(substitution, matches):
            called.append((substitution, matches))
            return [x for x in matches if not x.endswith('gif')]
        self.mkfile('Mädchen.txt')
        self.mkfile('Mädchen.gif')
        completer.ignore_some_completions_function = func
        readline.complete_internal(TAB)
        self.assertEqual(called,
            [(decompose('Mädchen.'), [decompose('Mädchen.gif'), decompose('Mädchen.txt')])])
        self.assertEqual(completion.line_buffer, decompose("Mädchen.txt "))


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

    def test_filename_quoting_function(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return text.replace(' ', '\\ ')
        self.mkfile('Mä dchen.txt')
        completer.filename_quoting_function = func
        completion.line_buffer = decompose('Mä')
        readline.complete_internal(TAB)
        self.assertEqual(called, [(decompose('Mä dchen.txt'), True, '')])
        self.assertEqual(completion.line_buffer, decompose("Mä\\ dchen.txt "))


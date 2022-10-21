# -*- coding: utf-8 -*-

import sys
import locale

if sys.version_info[0] < 3:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass

import os
import unittest
import unicodedata
import functools

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


def compose(text):
    # HFS Plus uses decomposed UTF-8
    if sys.platform != 'darwin':
        return text
    if sys.version_info[0] >= 3:
        return unicodedata.normalize('NFC', text)
    else:
        return unicodedata.normalize('NFC', text.decode('utf-8')).encode('utf-8')


def decompose(text):
    # HFS Plus uses decomposed UTF-8
    if sys.platform != 'darwin':
        return text
    if sys.version_info[0] >= 3:
        return unicodedata.normalize('NFD', text)
    else:
        return unicodedata.normalize('NFD', text.decode('utf-8')).encode('utf-8')


def utf8_only(func):
    # Skip tests unless UTF-8 locale
    def guard(*args, **kw):
        if locale.getpreferredencoding(False).upper() == 'UTF-8':
            return func(*args, **kw)
        else:
            sys.stderr.write('!')
            sys.stderr.flush()
    return functools.wraps(func)(guard)


class CompleterTests(unittest.TestCase):

    def setUp(self):
        reset()

    @utf8_only
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

    @utf8_only
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

    @utf8_only
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

    @utf8_only
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

    @utf8_only
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

    @utf8_only
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

    @utf8_only
    def test_filename_dequoting_function(self):
        def func(text, quote_char):
            called.append((text, quote_char))
            return text.replace('\\', '')
        self.mkfile('Mä dchen.txt')
        completer.filename_dequoting_function = func
        completer.filename_rewrite_hook = compose
        completion.line_buffer = 'Mä\\ '
        readline.complete_internal(TAB)
        if readline.readline_version() >= 0x0801:
            self.assertEqual(called, [('.', ''), ('Mä\\ ', ''), ('Mä\\ ', '')])
        else:
            self.assertEqual(called, [('.', ''), ('Mä\\ ', '')])
        self.assertEqual(completion.line_buffer, "'Mä dchen.txt' ")


class IgnoreSomeCompletionsFunctionTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.completer = filecomplete

    @utf8_only
    def test_ignore_some_completions_function(self):
        def func(substitution, matches):
            called.append((substitution, matches))
            return [x for x in matches if not x.endswith('gif')]
        self.mkfile('Mädchen.txt')
        self.mkfile('Mädchen.gif')
        completer.ignore_some_completions_function = func
        completer.filename_rewrite_hook = compose
        readline.complete_internal(TAB)
        self.assertEqual(called,
            [('Mädchen.', ['Mädchen.gif', 'Mädchen.txt'])])
        self.assertEqual(completion.line_buffer, "Mädchen.txt ")


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

    @utf8_only
    def test_filename_quoting_function(self):
        def func(text, single_match, quote_char):
            called.append((text, single_match, quote_char))
            return text.replace(' ', '\\ ')
        self.mkfile('Mä dchen.txt')
        completer.filename_quoting_function = func
        completer.filename_rewrite_hook = compose
        completion.line_buffer = 'Mä'
        readline.complete_internal(TAB)
        self.assertEqual(called, [('Mä dchen.txt', True, '')])
        self.assertEqual(completion.line_buffer, "Mä\\ dchen.txt ")


class FilenameRewriteHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.completer = filecomplete

    @utf8_only
    def test_filename_rewrite_hook(self):
        def func(filename):
            called.append(filename)
            return filename
        self.mkfile(decompose('Mädchen.txt'))
        completer.filename_rewrite_hook = func
        completion.line_buffer = 'M'
        readline.complete_internal(TAB)
        self.assertEqual(sorted(called), ['.', '..', decompose('Mädchen.txt')])
        self.assertEqual(completion.line_buffer, decompose("Mädchen.txt "))

    @utf8_only
    def test_compose_in_filename_rewrite_hook(self):
        def func(filename):
            called.append(filename)
            return compose(filename)
        self.mkfile(decompose('Mädchen.txt'))
        completer.filename_rewrite_hook = func
        completion.line_buffer = 'M'
        readline.complete_internal(TAB)
        self.assertEqual(sorted(called), ['.', '..', decompose('Mädchen.txt')])
        self.assertEqual(completion.line_buffer, "Mädchen.txt ")


class DirectoryRewriteHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.quote_characters = '\'"'
        completer.word_break_characters = ' \t\n"\''
        completer.filename_quote_characters = ' \t\n"\''
        completer.char_is_quoted_function = is_quoted
        completer.completer = filecomplete

    @utf8_only
    def test_directory_rewrite_hook(self):
        def func(dirname):
            called.append(dirname)
            return dirname.replace('\\', '')
        self.mkdir('Mä dchen')
        self.mkfile('Mä dchen/fred.txt')
        completer.directory_rewrite_hook = func
        completion.line_buffer = 'Mä\\ dchen/fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['Mä\\ dchen/'])
        self.assertEqual(completion.line_buffer, "'Mä\\ dchen/fred.txt' ")


class FilenameStatHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        called[:] = []
        completer.completer = filecomplete

    def test_filename_stat_hook(self):
        def func(filename):
            called.append(filename)
            return filename
        self.mkdir('fred')
        completer.filename_stat_hook = func
        completion.line_buffer = 'fr'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['fred'])
        self.assertEqual(completion.line_buffer, 'fred/')

    @utf8_only
    def test_filename_stat_hook_utf8(self):
        def func(filename):
            called.append(filename)
            return filename
        self.mkdir('Mädchen')
        completer.filename_stat_hook = func
        completer.filename_rewrite_hook = compose
        completion.line_buffer = 'M'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['Mädchen'])
        self.assertEqual(completion.line_buffer, 'Mädchen/')

    @utf8_only
    def test_decompose_in_filename_stat_hook(self):
        def func(filename):
            called.append(filename)
            return filename # XXX
        self.mkdir(decompose('Mädchen'))
        completer.filename_stat_hook = func
        completer.filename_rewrite_hook = compose
        completion.line_buffer = 'M'
        readline.complete_internal(TAB)
        self.assertEqual(called, ['Mädchen'])
        self.assertEqual(completion.line_buffer, 'Mädchen/')


class APFSComplianceTests(JailSetup):

    @utf8_only
    def test_list_decomposed_file(self):
        self.mkfile(decompose('Mädchen.txt'))
        self.assertEqual(os.listdir(os.curdir), [decompose('Mädchen.txt')])

    @utf8_only
    def test_locate_decomposed_file(self):
        self.mkfile(decompose('Mädchen.txt'))
        self.assertTrue(os.path.exists('Mädchen.txt'))

    @utf8_only
    def test_open_decomposed_file(self):
        self.mkfile(decompose('Mädchen.txt'))
        with open('Mädchen.txt', 'rt') as f:
            self.assertNotEqual(f, None)


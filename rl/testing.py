"""Test helpers."""

import unittest
import os
import tempfile
import shutil

from os.path import realpath, isdir

from rl import completer
from rl import completion
from rl import history

DEFAULT_DELIMS = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'


def reset_completer():
    completer.quote_characters = ''
    completer.word_break_characters = DEFAULT_DELIMS
    completer.special_prefixes = ''
    completer.filename_quote_characters = ''
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
    completion.begidx = 0
    completion.endidx = 0
    completion.line_buffer = ''
    completion.completion_type = ''
    completion.append_character = ' '
    completion.suppress_append = False
    completion.quote_character = ''
    completion.suppress_quote = False
    completion.found_quote = False
    completion.filename_completion_desired = False
    completion.filename_quoting_desired = True


def reset_history():
    history.clear()
    history.max_entries = -1


def reset():
    reset_completer()
    reset_completion()
    reset_history()


class JailSetup(unittest.TestCase):

    origdir = None
    tempdir = None

    def setUp(self):
        self.origdir = os.getcwd()
        self.tempdir = realpath(tempfile.mkdtemp())
        os.chdir(self.tempdir)

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.origdir is not None:
            if isdir(self.origdir):
                os.chdir(self.origdir)
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)

    def mkdir(self, *names):
        for name in names:
            os.mkdir(name)

    def mkfile(self, *names):
        for name in names:
            f = open(name, 'wt')
            f.write('23\n')
            f.close()


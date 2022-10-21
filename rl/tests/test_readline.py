import unittest
import sys
import os

from os.path import isfile, expanduser

from rl import readline
from rl.testing import reset
from rl.testing import JailSetup


class ReadlineTests(JailSetup):
    # XXX You will lose your ~/.history file when you run these tests

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.histfile = expanduser('~/.history')
        self.initfile = expanduser('~/.$$$')
        self.remove_files()

    def tearDown(self):
        self.remove_files()
        JailSetup.tearDown(self)

    def remove_files(self):
        if isfile(self.histfile):
            os.remove(self.histfile)
        if isfile(self.initfile):
            os.remove(self.initfile)

    def test_AAA_setup_init_file(self):
        self.mkfile(self.initfile)
        readline.read_init_file(self.initfile)

    def test_readline_version(self):
        self.assertNotEqual(readline.readline_version(), 0)

    def test_stuff_and_read(self):
        c = 'x'
        self.assertEqual(readline.stuff_char(c), True)
        self.assertEqual(readline.read_key(), c)

    def test_tilde_expand_None(self):
        self.assertRaises(TypeError, readline.tilde_expand, None)

    def test_tilde_expand_empty_string(self):
        self.assertEqual(readline.tilde_expand(''), '')

    def test_parse_and_bind_None(self):
        self.assertRaises(TypeError, readline.parse_and_bind, None)

    def test_parse_and_bind_empty_string(self):
        self.assertEqual(readline.parse_and_bind(''), None)

    def test_read_initfile_noarg(self):
        self.mkfile('my_init')
        self.mkfile(self.initfile)
        readline.read_init_file()

    def test_read_initfile_None(self):
        self.mkfile('my_init')
        self.mkfile(self.initfile)
        readline.read_init_file(None)

    def test_read_initfile_empty_string(self):
        self.mkfile('my_init')
        self.mkfile(self.initfile)
        self.assertRaises(IOError, readline.read_init_file, '')

    def test_read_history_file_noarg(self):
        self.mkfile(self.histfile)
        readline.read_history_file()

    def test_read_history_file_None(self):
        self.mkfile(self.histfile)
        readline.read_history_file(None)

    def test_read_history_file_empty_string(self):
        self.mkfile(self.histfile)
        self.assertRaises(IOError, readline.read_history_file, '')

    def test_write_history_file_noarg(self):
        readline.write_history_file()
        self.assertTrue(isfile(self.histfile))

    def test_write_history_file_None(self):
        readline.write_history_file(None)
        self.assertTrue(isfile(self.histfile))

    def test_write_history_file_empty_string(self):
        self.assertRaises(IOError, readline.write_history_file, '')

    def test_redisplay_keyword_arg(self):
        self.assertRaises(TypeError, readline.redisplay, force=True)

    def test_auto_history_default(self):
        self.assertEqual(readline.get_auto_history(), True)

    def test_auto_history(self):
        readline.set_auto_history(False)
        self.assertEqual(readline.get_auto_history(), False)
        readline.set_auto_history(True)
        self.assertEqual(readline.get_auto_history(), True)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


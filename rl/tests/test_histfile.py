import unittest
import sys
import os

from os.path import isfile, expanduser, abspath

from rl import history
from rl import readline
from rl.testing import JailSetup
from rl.testing import reset


class HistoryFileTests(JailSetup):
    # XXX You will lose your ~/.history file when you run these tests

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.histfile = expanduser('~/.history')
        self.remove_histfile()

    def tearDown(self):
        self.remove_histfile()
        JailSetup.tearDown(self)

    def remove_histfile(self):
        if isfile(self.histfile):
            os.remove(self.histfile)

    def test_no_histfile(self):
        self.assertEqual(isfile(self.histfile), False)

    def test_read_file_raises_exception(self):
        self.assertRaises(IOError,
            history.read_file, 'my_history', raise_exc=True)

    def test_write_file_raises_exception(self):
        self.assertRaises(IOError,
            history.write_file, '~/~/.my_history', raise_exc=True)

    def test_append_file_raises_exception(self):
        self.assertRaises(IOError,
            history.append_file, 0, '~/~/.my_history', raise_exc=True)

    def test_read_relative(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_relative(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history', raise_exc=True)
        self.assertTrue(isfile('my_history'))

    def test_append_relative(self):
        history.write_file('my_history', raise_exc=True)
        history.append('fred')
        history.append('wilma')
        history.append_file(2, 'my_history')
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_read_abspath(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.read_file(abspath('my_history'), raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_abspath(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(abspath('my_history'), raise_exc=True)
        self.assertTrue(isfile(abspath('my_history')))
        self.assertTrue(isfile('my_history'))

    def test_append_abspath(self):
        history.write_file('my_history', raise_exc=True)
        history.append('fred')
        history.append('wilma')
        history.append_file(2, abspath('my_history'))
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_read_default_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(self.histfile, raise_exc=True)
        history.clear()
        history.read_file(raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_default_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(raise_exc=True)
        self.assertTrue(isfile(self.histfile))

    def test_append_default_name(self):
        history.write_file(self.histfile, raise_exc=True)
        history.append('fred')
        history.append('wilma')
        history.append_file(2)
        history.clear()
        history.read_file(self.histfile, raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_read_None_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(self.histfile, raise_exc=True)
        history.clear()
        history.read_file(None, raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_None_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(None, raise_exc=True)
        self.assertTrue(isfile(self.histfile))

    def test_append_None_name(self):
        history.write_file(self.histfile, raise_exc=True)
        history.append('fred')
        history.append('wilma')
        history.append_file(2, None)
        history.clear()
        history.read_file(self.histfile, raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_read_empty_string(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(self.histfile, raise_exc=True)
        history.clear()
        self.assertRaises(IOError, history.read_file, '', raise_exc=True)

    def test_write_empty_string(self):
        history.append('fred')
        history.append('wilma')
        self.assertRaises(IOError, history.write_file, '', raise_exc=True)

    def test_append_empty_string(self):
        history.write_file(self.histfile, raise_exc=True)
        history.append('fred')
        history.append('wilma')
        self.assertRaises(IOError, history.append_file, 1, '', raise_exc=True)

    def test_read_tilde_expanded(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(self.histfile, raise_exc=True)
        history.clear()
        history.read_file('~/.history', raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_tilde_expanded(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('~/.history', raise_exc=True)
        self.assertTrue(isfile(self.histfile))

    def test_append_tilde_expanded(self):
        history.write_file(self.histfile, raise_exc=True)
        history.append('fred')
        history.append('wilma')
        history.append_file(2, '~/.history')
        history.clear()
        history.read_file(self.histfile, raise_exc=True)
        self.assertEqual(len(history), 2)

    if sys.version_info[0] >= 3:

        def test_read_bytes_name(self):
            history.append('fred')
            history.append('wilma')
            history.write_file(bytes('my_history', sys.getfilesystemencoding()), raise_exc=True)
            history.clear()
            history.read_file(bytes('my_history', sys.getfilesystemencoding()), raise_exc=True)
            self.assertEqual(len(history), 2)

        def test_write_bytes_name(self):
            history.append('fred')
            history.append('wilma')
            history.write_file(bytes('my_history', sys.getfilesystemencoding()), raise_exc=True)
            self.assertTrue(isfile('my_history'))

        def test_append_bytes_name(self):
            history.write_file(bytes('my_history', sys.getfilesystemencoding()), raise_exc=True)
            history.append('fred')
            history.append('wilma')
            history.append_file(2, bytes('my_history', sys.getfilesystemencoding()))
            history.clear()
            history.read_file(bytes('my_history', sys.getfilesystemencoding()), raise_exc=True)
            self.assertEqual(len(history), 2)

    def test_read_file_stifled(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        history.append('dino')
        self.assertEqual(len(history), 7)
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.max_entries = 5
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'betty')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'bammbamm')
        self.assertEqual(history[4], 'dino')
        self.assertEqual(len(history), 5)

    def test_write_file_stifled(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        history.append('dino')
        self.assertEqual(len(history), 7)
        history.max_entries = 5
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.max_entries = -1
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'betty')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'bammbamm')
        self.assertEqual(history[4], 'dino')
        self.assertEqual(len(history), 5)

    def test_write_file_replaces_file(self):
        history.append('fred')
        history.append('wilma')
        history.append('pebbles')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.append('barney')
        history.append('betty')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'betty')

    def test_write_file_truncates_file(self):
        history.append('fred')
        history.append('wilma')
        history.append('pebbles')
        history.max_file = 2
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'pebbles')

    def test_append_file(self):
        history.append('fred')
        history.append('wilma')
        history.append('pebbles')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.append('barney')
        history.append('betty')
        history.append('bammbamm')
        history.append_file(2, 'my_history')
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'wilma')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'betty')
        self.assertEqual(history[4], 'bammbamm')

    def test_append_file_truncates_file(self):
        history.append('fred')
        history.append('wilma')
        history.append('pebbles')
        history.write_file('my_history', raise_exc=True)
        history.clear()
        history.append('barney')
        history.append('betty')
        history.append('bammbamm')
        history.max_file = 3
        history.append_file(2, 'my_history')
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], 'pebbles')
        self.assertEqual(history[1], 'betty')
        self.assertEqual(history[2], 'bammbamm')


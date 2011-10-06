import unittest
import sys
import os

from os.path import isfile, expanduser, abspath

from rl import history
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


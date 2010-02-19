import unittest
import sys
import os

from os.path import isfile, expanduser

from rl import history
from rl.testing import JailSetup
from rl.testing import reset


class HistoryTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_length(self):
        self.assertEqual(history.length, -1)
        history.length = 100
        self.assertEqual(history.length, 100)

    def test_add_item(self):
        self.assertEqual(len(history), 0)
        history.add_item('fred')
        self.assertEqual(len(history), 1)

    def test_append(self):
        self.assertEqual(len(history), 0)
        history.append('fred')
        self.assertEqual(len(history), 1)

    def test__len__(self):
        self.assertEqual(len(history), 0)
        history.append('fred')
        self.assertEqual(len(history), 1)
        history.append('wilma')
        self.assertEqual(len(history), 2)

    def test_get_item(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual(history.get_item(0), 'fred')
        self.assertEqual(history.get_item(1), 'wilma')
        self.assertEqual(history.get_item(2), 'barney')
        self.assertEqual(history.get_item(3), 'betty')

    def test__getitem__(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'wilma')
        self.assertEqual(history[2], 'barney')
        self.assertEqual(history[3], 'betty')

    def test_remove_item(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        history.remove_item(1)
        self.assertEqual(len(history), 3)
        self.assertEqual(history.get_item(0), 'fred')
        self.assertEqual(history.get_item(1), 'barney')
        self.assertEqual(history.get_item(2), 'betty')

    def test__delitem__(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        del history[1]
        self.assertEqual(len(history), 3)
        self.assertEqual(history.get_item(0), 'fred')
        self.assertEqual(history.get_item(1), 'barney')
        self.assertEqual(history.get_item(2), 'betty')

    def test_replace_item(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        history.replace_item(1, 'pebbles')
        self.assertEqual(len(history), 4)
        self.assertEqual(history.get_item(0), 'fred')
        self.assertEqual(history.get_item(1), 'pebbles')
        self.assertEqual(history.get_item(2), 'barney')
        self.assertEqual(history.get_item(3), 'betty')

    def test__setitem__(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        history[1] = 'pebbles'
        self.assertEqual(len(history), 4)
        self.assertEqual(history.get_item(0), 'fred')
        self.assertEqual(history.get_item(1), 'pebbles')
        self.assertEqual(history.get_item(2), 'barney')
        self.assertEqual(history.get_item(3), 'betty')

    def test_negative_pos(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual(history[-4], 'fred')
        self.assertEqual(history[-3], 'wilma')
        self.assertEqual(history[-2], 'barney')
        self.assertEqual(history[-1], 'betty')

    def test_out_of_range_pos(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertRaises(IndexError, history.get_item, 4)
        self.assertRaises(IndexError, history.get_item, -5)

    def test_invalid_pos(self):
        self.assertRaises(TypeError, history.get_item, 'foo')
        self.assertRaises(TypeError, history.get_item, None)

    def test_bool_is_int(self):
        self.assertRaises(IndexError, history.get_item, False)
        history.append('fred')
        self.assertEqual(history.get_item(False), 'fred')

    def test_slots(self):
        self.assertRaises(AttributeError, setattr, history, 'foo', 1)

    def test_clear(self):
        history.append('fred')
        history.clear()
        self.assertEqual(len(history), 0)


class HistoryFileTests(JailSetup):
    # You will lose your ~/.history file when you run these tests

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.histfile = expanduser('~/.history')
        self._remove_histfile()

    def tearDown(self):
        self._remove_histfile()
        JailSetup.tearDown(self)

    def _remove_histfile(self):
        if isfile(self.histfile):
            os.remove(self.histfile)

    def test_no_histfile(self):
        self.assertEqual(isfile(self.histfile), False)

    def test_write_file(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history')
        self.failUnless(isfile('my_history'))

    def test_write_default_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file()
        self.failUnless(isfile(self.histfile))

    def test_write_None_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(None)
        self.failUnless(isfile(self.histfile))

    def test_read_file(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history')
        history.clear()
        history.read_file('my_history')
        self.assertEqual(len(history), 2)

    def test_read_default_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file()
        history.clear()
        history.read_file()
        self.assertEqual(len(history), 2)

    def test_read_None_name(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(None)
        history.clear()
        history.read_file(None)
        self.assertEqual(len(history), 2)

    if sys.version_info[0] >= 3:

        def test_write_bytes_name(self):
            history.append('fred')
            history.append('wilma')
            history.write_file(bytes('my_history', sys.getfilesystemencoding()))
            self.failUnless(isfile('my_history'))

        def test_read_bytes_name(self):
            history.append('fred')
            history.append('wilma')
            history.write_file(bytes('my_history', sys.getfilesystemencoding()))
            history.clear()
            history.read_file(bytes('my_history', sys.getfilesystemencoding()))
            self.assertEqual(len(history), 2)


import unittest

from rl import history


class HistoryTests(unittest.TestCase):

    def setUp(self):
        history.clear()

    def test_length(self):
        self.assertEqual(history.length, -1)
        history.length = 100
        self.assertEqual(history.length, 100)

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
        self.assertRaises(TypeError, history.get_item, False)


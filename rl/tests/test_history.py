import unittest

from rl import history


class HistoryTests(unittest.TestCase):

    def setUp(self):
        history.clear()

    def test_add(self):
        self.assertEqual(history.current_length, 0)
        history.add('fred')
        self.assertEqual(history.current_length, 1)

    def test__len__(self):
        history.add('fred')
        self.assertEqual(len(history), 1)
        history.add('wilma')
        self.assertEqual(len(history), 2)

    def test_base(self):
        history.add('fred')
        self.assertEqual(history.base, 1)
        history.add('wilma')
        self.assertEqual(history.base, 1)

    def test_get_item(self):
        history.add('fred')
        history.add('wilma')
        history.add('barney')
        history.add('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual(history.base, 1)
        self.assertEqual(history.get_item(1), 'fred') # history.base-based here
        self.assertEqual(history.get_item(2), 'wilma')
        self.assertEqual(history.get_item(3), 'barney')
        self.assertEqual(history.get_item(4), 'betty')

    def test_remove_item(self):
        history.add('fred')
        history.add('wilma')
        history.add('barney')
        history.add('betty')
        self.assertEqual(len(history), 4)
        history.remove_item(1) # Zero-based here!
        self.assertEqual(len(history), 3)
        self.assertEqual(history.base, 1)
        self.assertEqual(history.get_item(1), 'fred')
        self.assertEqual(history.get_item(2), 'barney')
        self.assertEqual(history.get_item(3), 'betty')

    def test_replace_item(self):
        history.add('fred')
        history.add('wilma')
        history.add('barney')
        history.add('betty')
        self.assertEqual(len(history), 4)
        history.replace_item(1, 'pebbles') # Zero-based here!
        self.assertEqual(len(history), 4)
        self.assertEqual(history.base, 1)
        self.assertEqual(history.get_item(1), 'fred')
        self.assertEqual(history.get_item(2), 'pebbles')
        self.assertEqual(history.get_item(3), 'barney')
        self.assertEqual(history.get_item(4), 'betty')


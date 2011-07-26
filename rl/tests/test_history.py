import unittest

from rl import history
from rl.testing import reset


class HistoryTests(unittest.TestCase):

    def setUp(self):
        reset()

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

    def test__iter__empty(self):
        self.assertEqual(len(history), 0)
        self.assertEqual([x for x in history], [])

    def test__iter__items(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual([x for x in history], ['fred', 'wilma', 'barney', 'betty'])

    def test__reversed__empty(self):
        self.assertEqual(len(history), 0)
        self.assertEqual([x for x in reversed(history)], [])

    def test__reversed__items(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertEqual([x for x in reversed(history)], ['betty', 'barney', 'wilma', 'fred'])

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

    def test__delitem__(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        del history[1]
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'betty')

    def test__setitem__(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        history[1] = 'pebbles'
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'pebbles')
        self.assertEqual(history[2], 'barney')
        self.assertEqual(history[3], 'betty')

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

    def test_list_long_pos(self):
        list = ['fred']
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0L], 'fred')
        self.assertEqual(list[-1L], 'fred')

    def test_history_long_pos(self):
        history.append('fred')
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0L], 'fred')
        self.assertEqual(history[-1L], 'fred')

    def test_out_of_range_pos(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual(len(history), 4)
        self.assertRaises(IndexError, history.__getitem__, 4)
        self.assertRaises(IndexError, history.__getitem__, -5)

    def test_invalid_pos(self):
        self.assertRaises(TypeError, history.__getitem__, 'foo')
        self.assertRaises(TypeError, history.__getitem__, None)

    def test_bools_are_ints(self):
        self.assertRaises(IndexError, history.__getitem__, False)
        history.append('fred')
        self.assertEqual(history[False], 'fred')

    def test_slots(self):
        self.assertRaises(AttributeError, setattr, history, 'foo', 1)

    def test_clear(self):
        history.append('fred')
        history.clear()
        self.assertEqual(len(history), 0)

    def test_max_entries(self):
        self.assertEqual(history.max_entries, -1)
        history.max_entries = 300
        self.assertEqual(history.max_entries, 300)
        history.max_entries = 200
        self.assertEqual(history.max_entries, 200)
        history.max_entries = 100
        self.assertEqual(history.max_entries, 100)
        history.max_entries = 1
        self.assertEqual(history.max_entries, 1)
        history.max_entries = 0
        self.assertEqual(history.max_entries, 0)
        history.max_entries = -1
        self.assertEqual(history.max_entries, -1)
        history.max_entries = -2
        self.assertEqual(history.max_entries, -1)
        history.max_entries = -3
        self.assertEqual(history.max_entries, -1)


class HistoryStiflingTests(unittest.TestCase):

    def setUp(self):
        reset()
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')

    def test_fixture(self):
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'wilma')
        self.assertEqual(history[2], 'barney')
        self.assertEqual(history[3], 'betty')
        self.assertEqual(history[4], 'pebbles')
        self.assertEqual(len(history), 5)

    def test_stifled(self):
        history.max_entries = 5
        # Extend history beyond 5 entries
        history.append('bammbamm')
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'betty')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bammbamm')
        self.assertEqual(len(history), 5)
        # Add one more
        history.append('dino')
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'betty')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'bammbamm')
        self.assertEqual(history[4], 'dino')
        self.assertEqual(len(history), 5)

    def test_unstifled(self):
        history.max_entries = -1
        # Extend history beyond 5 entries
        history.append('bammbamm')
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'wilma')
        self.assertEqual(history[2], 'barney')
        self.assertEqual(history[3], 'betty')
        self.assertEqual(history[4], 'pebbles')
        self.assertEqual(history[5], 'bammbamm')
        self.assertEqual(len(history), 6)

    def test_is_stifled(self):
        history.max_entries = 5
        self.assertEqual(history.max_entries, 5)
        history.max_entries = -1
        self.assertEqual(history.max_entries, -1)

    def test_stifle_truncates_existing(self):
        history.max_entries = -1
        # Extend history beyond 5 entries
        history.append('bammbamm')
        history.append('dino')
        self.assertEqual(len(history), 7)
        # Now stifle
        history.max_entries = 5
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'betty')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'bammbamm')
        self.assertEqual(history[4], 'dino')
        self.assertEqual(len(history), 5)

    def test_remove(self):
        history.max_entries = 5
        history.append('bammbamm')
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'betty')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bammbamm')
        del history[2]
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'pebbles')
        self.assertEqual(history[3], 'bammbamm')
        self.assertEqual(len(history), 4)
        del history[0]
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'pebbles')
        self.assertEqual(history[2], 'bammbamm')
        self.assertEqual(len(history), 3)
        del history[-1]
        self.assertEqual(history[0], 'barney')
        self.assertEqual(history[1], 'pebbles')
        self.assertEqual(len(history), 2)

    def test_replace(self):
        history.max_entries = 5
        history.append('bammbamm')
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'betty')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bammbamm')
        history[2] = 'dino'
        self.assertEqual(history[0], 'wilma')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'dino')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bammbamm')
        history[0] = 'hopper'
        self.assertEqual(history[0], 'hopper')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'dino')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bammbamm')
        history[-1] = 'bedrock'
        self.assertEqual(history[0], 'hopper')
        self.assertEqual(history[1], 'barney')
        self.assertEqual(history[2], 'dino')
        self.assertEqual(history[3], 'pebbles')
        self.assertEqual(history[4], 'bedrock')

    def test__iter__items(self):
        history.max_entries = 5
        history.append('bammbamm')
        self.assertEqual([x for x in history], ['wilma', 'barney', 'betty', 'pebbles', 'bammbamm'])
        history.append('dino')
        self.assertEqual([x for x in history], ['barney', 'betty', 'pebbles', 'bammbamm', 'dino'])
        history[0] = 'hopper'
        self.assertEqual([x for x in history], ['hopper', 'betty', 'pebbles', 'bammbamm', 'dino'])

    def test__reversed__items(self):
        history.max_entries = 5
        history.append('bammbamm')
        self.assertEqual([x for x in reversed(history)], ['bammbamm', 'pebbles', 'betty', 'barney', 'wilma'])
        history.append('dino')
        self.assertEqual([x for x in reversed(history)], ['dino', 'bammbamm', 'pebbles', 'betty', 'barney'])
        history[0] = 'hopper'
        self.assertEqual([x for x in reversed(history)], ['dino', 'bammbamm', 'pebbles', 'betty', 'hopper'])


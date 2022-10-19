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
        self.assertEqual(history[-4], 'fred')
        self.assertEqual(history[-3], 'wilma')
        self.assertEqual(history[-2], 'barney')
        self.assertEqual(history[-1], 'betty')

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
        del history[-2]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'betty')

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
        history[-2] = 'bammbamm'
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0], 'fred')
        self.assertEqual(history[1], 'pebbles')
        self.assertEqual(history[2], 'bammbamm')
        self.assertEqual(history[3], 'betty')

    #def test_list_long_pos(self):
    #    list = ['fred']
    #    self.assertEqual(len(list), 1)
    #    self.assertEqual(list[0L], 'fred')
    #    self.assertEqual(list[-1L], 'fred')

    #def test_history_long_pos(self):
    #    history.append('fred')
    #    self.assertEqual(len(history), 1)
    #    self.assertEqual(history[0L], 'fred')
    #    self.assertEqual(history[-1L], 'fred')

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

    def test_zero_disables_history(self):
        self.assertEqual(len(history), 0)
        history.max_entries = 0
        history.append('fred')
        history.append('barney')
        self.assertEqual(len(history), 0)

    def test_get_slice(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertRaises(TypeError, history.__getitem__, slice(2, -1))

    def test_set_slice(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertRaises(TypeError, history.__setitem__, slice(2, -1), ['dino'])

    def test_del_slice(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertRaises(TypeError, history.__delitem__, slice(2, -1))

    def test_max_file(self):
        self.assertEqual(history.max_file, -1)
        history.max_file = 300
        self.assertEqual(history.max_file, 300)
        history.max_file = 1
        self.assertEqual(history.max_file, 1)
        history.max_file = 0
        self.assertEqual(history.max_file, 0)
        history.max_file = -1
        self.assertEqual(history.max_file, -1)
        history.max_file = -2
        self.assertEqual(history.max_file, -1)
        history.max_file = -3
        self.assertEqual(history.max_file, -1)

    def test_auto_history(self):
        self.assertEqual(history.auto, True)
        history.auto = False
        self.assertEqual(history.auto, False)
        history.auto = True
        self.assertEqual(history.auto, True)


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


class HistoryIteratorTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_iter_class(self):
        i = iter(history)
        self.assertEqual(i.__class__.__name__, 'historyiterator')

    def test_iterate(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual([x for x in history], ['fred', 'wilma', 'barney', 'betty'])

    def test_iterate_empty(self):
        self.assertEqual([x for x in history], [])

    def test_iterate_exhausted(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        i = iter(history)
        self.assertEqual([x for x in i], ['fred', 'wilma', 'barney', 'betty'])
        self.assertRaises(StopIteration, next, i)

    def test_iterate_iterator(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual([x for x in iter(iter(history))], ['fred', 'wilma', 'barney', 'betty'])
        list = ['a', 'b', 'c', 'd']
        self.assertEqual([x for x in iter(iter(list))], ['a', 'b', 'c', 'd'])

    def test_reversed_iterator(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertRaises(TypeError, reversed, iter(history))
        list = ['a', 'b', 'c', 'd']
        self.assertRaises(TypeError, reversed, iter(list))

    def test_shrinking_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(history):
            if n % 2 == 0 and 0 < n < len(history):
                del history[n]

    def test_growing_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(history):
            if n % 2 == 0 and 0 < n:
                history.append('dino')

    def test_cleared_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(history):
            if n == 3:
                history.clear()

    def test_length_hint(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        i = iter(history)
        self.assertEqual(i.__length_hint__(), len(history))
        for n, x in enumerate(i):
            self.assertEqual(i.__length_hint__(), len(history)-n-1)


class HistoryReverseIteratorTests(unittest.TestCase):

    def setUp(self):
        reset()

    def test_iter_class(self):
        i = reversed(history)
        self.assertEqual(i.__class__.__name__, 'historyreverseiterator')

    def test_iterate(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual([x for x in reversed(history)], ['betty', 'barney', 'wilma', 'fred'])

    def test_iterate_empty(self):
        self.assertEqual([x for x in reversed(history)], [])

    def test_iterate_exhausted(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        i = reversed(history)
        self.assertEqual([x for x in i], ['betty', 'barney', 'wilma', 'fred'])
        self.assertRaises(StopIteration, next, i)

    def test_iterate_iterator(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertEqual([x for x in iter(reversed(history))], ['betty', 'barney', 'wilma', 'fred'])
        list = ['a', 'b', 'c', 'd']
        self.assertEqual([x for x in iter(reversed(list))], ['d', 'c', 'b', 'a'])

    def test_reversed_iterator(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        self.assertRaises(TypeError, reversed, reversed(history))
        list = ['a', 'b', 'c', 'd']
        self.assertRaises(TypeError, reversed, reversed(list))

    def test_shrinking_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(reversed(history)):
            if n % 2 == 0 and 0 < n < len(history):
                del history[n]

    def test_growing_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(reversed(history)):
            if n % 2 == 0 and 0 < n:
                history.append('dino')

    def test_cleared_seq(self):
        # Don't crash if the history is modifed while iterating
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        history.append('pebbles')
        history.append('bammbamm')
        for n, x in enumerate(reversed(history)):
            if n == 3:
                history.clear()

    def test_length_hint(self):
        history.append('fred')
        history.append('wilma')
        history.append('barney')
        history.append('betty')
        i = reversed(history)
        self.assertEqual(i.__length_hint__(), len(history))
        for n, x in enumerate(i):
            self.assertEqual(i.__length_hint__(), len(history)-n-1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


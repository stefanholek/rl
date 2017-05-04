import unittest
import operator


class SortTests(unittest.TestCase):

    def test_sort_key(self):
        l = ['foo.so.6.3', 'foo.so.6', 'foo.so']
        l.sort(key=lambda x: len(x))
        self.assertEqual(l, ['foo.so', 'foo.so.6', 'foo.so.6.3'])

    def test_sort_attr(self):
        l = ['foo.so.6.3', 'foo.so.6', 'foo.so']
        l.sort(key=operator.attrgetter('__len__'))
        self.assertEqual(l, ['foo.so', 'foo.so.6', 'foo.so.6.3'])


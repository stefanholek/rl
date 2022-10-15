import unittest
import operator


class SortTests(unittest.TestCase):

    def test_sort_key(self):
        l = ['foo.so.6.3', 'foo.so.6', 'foo.so']
        l.sort(key=lambda x: len(x))
        self.assertEqual(l, ['foo.so', 'foo.so.6', 'foo.so.6.3'])

    # Stopped working in Python 3.8
    #
    # Traceback (most recent call last):
    #   File "/Users/stefan/sandbox/rl/rl/tests/test_setup.py", line 14, in test_sort_attr
    #     l.sort(key=operator.attrgetter('__len__'))
    # TypeError: '<' not supported between instances of 'method-wrapper' and 'method-wrapper'
    #
    #def test_sort_attr(self):
    #    l = ['foo.so.6.3', 'foo.so.6', 'foo.so']
    #    l.sort(key=operator.attrgetter('__len__'))
    #    self.assertEqual(l, ['foo.so', 'foo.so.6', 'foo.so.6.3'])


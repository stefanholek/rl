import unittest

from rl import generator
from rl import print_exc


class GeneratorTests(unittest.TestCase):

    def test_generator_factory(self):

        def complete(text):
            """Test completer"""
            return ['foo', 'bar', 'baz']

        self.assertEqual(complete.__name__, 'complete')
        self.assertEqual(complete.__doc__, 'Test completer')

        g = generator(complete)
        self.assertEqual(g.__name__, 'complete')
        self.assertEqual(g.__doc__, 'Test completer')

        match = g('test', 0)
        self.assertEqual(match, 'foo')
        match = g('test', 1)
        self.assertEqual(match, 'bar')
        match = g('test', 2)
        self.assertEqual(match, 'baz')
        match = g('test', 3)
        self.assertEqual(match, None)

    def test_function_decorator(self):

        @generator
        def complete(text):
            """Test completer"""
            return ['foo', 'bar', 'baz']

        self.assertEqual(complete.__name__, 'complete')
        self.assertEqual(complete.__doc__, 'Test completer')

        match = complete('test', 0)
        self.assertEqual(match, 'foo')
        match = complete('test', 1)
        self.assertEqual(match, 'bar')
        match = complete('test', 2)
        self.assertEqual(match, 'baz')
        match = complete('test', 3)
        self.assertEqual(match, None)

    def test_method_decorator(self):

        class Complete(object):
            @generator
            def complete(self, text):
                """Test completer"""
                return ['foo', 'bar', 'baz']

        complete = Complete().complete
        self.assertEqual(complete.__name__, 'complete')
        self.assertEqual(complete.__doc__, 'Test completer')

        match = complete('test', 0)
        self.assertEqual(match, 'foo')
        match = complete('test', 1)
        self.assertEqual(match, 'bar')
        match = complete('test', 2)
        self.assertEqual(match, 'baz')
        match = complete('test', 3)
        self.assertEqual(match, None)

    def test_bad_arguments(self):

        @generator
        def complete(text):
            """Test completer"""
            return ['foo', 'bar', 'baz']

        self.assertRaises(IndexError, complete)
        self.assertRaises(KeyError, complete, 'test')
        self.assertRaises(KeyError, complete, 'test', 'foo')
        self.assertRaises(KeyError, complete, 1)
        self.assertRaises(KeyError, complete, 0, 1)
        self.assertRaises(KeyError, complete, 0, 1, 2)

    def test_bad_completer(self):

        @generator
        def complete(text):
            """Test completer"""
            return None

        self.assertRaises(TypeError, complete, 'test', 0)

    def test_separate_state(self):

        @generator
        def complete_1(text):
            return ['foo', 'bar', 'baz']

        @generator
        def complete_2(text):
            return ['fred', 'barney', 'wilma', 'betty']

        self.assertEqual(complete_1('test', 0), 'foo')
        self.assertEqual(complete_2('test', 0), 'fred')
        self.assertEqual(complete_1('test', 1), 'bar')
        self.assertEqual(complete_2('test', 1), 'barney')
        self.assertEqual(complete_1('test', 2), 'baz')
        self.assertEqual(complete_2('test', 2), 'wilma')
        self.assertEqual(complete_1('test', 3), None)
        self.assertEqual(complete_2('test', 3), 'betty')
        self.assertEqual(complete_1('test', 4), None)
        self.assertEqual(complete_2('test', 4), None)

    def test_wrap_callable_object(self):

        class Complete(object):
            """Test completer"""

            def __call__(self, text):
                return ['foo', 'bar', 'baz']

        g = generator(Complete())
        self.assertEqual(g.__name__, 'Complete')
        self.assertEqual(g.__doc__, 'Test completer')

        match = g('test', 0)
        self.assertEqual(match, 'foo')


class PrintExcTests(unittest.TestCase):

    def test_print_exc(self):

        def complete(text):
            """Test completer"""
            return []

        p = print_exc(complete)
        self.assertEqual(p.__name__, 'complete')
        self.assertEqual(p.__doc__, 'Test completer')

        self.assertEqual(p('test'), [])

    def test_function_decorator(self):

        @print_exc
        def complete(text):
            """Test completer"""
            return []

        self.assertEqual(complete.__name__, 'complete')
        self.assertEqual(complete.__doc__, 'Test completer')

        self.assertEqual(complete('test'), [])

    def test_method_decorator(self):

        class Complete(object):
            @print_exc
            def complete(self, text):
                """Test completer"""
                return []

        complete = Complete().complete
        self.assertEqual(complete.__name__, 'complete')
        self.assertEqual(complete.__doc__, 'Test completer')

        self.assertEqual(complete('test'), [])


import unittest

from rl import readline


class ReadlineTests(unittest.TestCase):

    def test_readline_version(self):
        self.assertNotEqual(readline.readline_version(), 0)

    def test_stuff_and_read(self):
        c = 'x'
        self.assertEqual(readline.stuff_char(c), True)
        self.assertEqual(readline.read_key(), c)

    def test_tilde_expand_None(self):
        self.assertRaises(TypeError, readline.tilde_expand, None)

    def test_tilde_expand_empty_string(self):
        self.assertEqual(readline.tilde_expand(''), '')

    def test_parse_and_bind_None(self):
        self.assertRaises(TypeError, readline.parse_and_bind, None)

    def test_parse_and_bind_empty_string(self):
        self.assertEqual(readline.parse_and_bind(''), None)


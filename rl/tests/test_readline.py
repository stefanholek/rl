import unittest

from rl import readline


class ReadlineTests(unittest.TestCase):

    def test_readline_version(self):
        self.failIfEqual(readline.readline_version(), 0)

    def test_stuff_and_read(self):
        c = 'x'
        self.assertEqual(readline.stuff_char(c), True)
        self.assertEqual(readline.read_key(), c)

import unittest

from rl import readline


class ReadlineTests(unittest.TestCase):

    def test_readline_version(self):
        self.failIfEqual(readline.readline_version(), 0)


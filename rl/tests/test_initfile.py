import unittest
import sys
import os

from os.path import isfile, expanduser, abspath

from rl import completer
from rl.testing import JailSetup
from rl.testing import reset


class ReadInitFileTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.initfile = expanduser('~/.$$$')
        self.remove_initfile()

    def tearDown(self):
        self.remove_initfile()
        JailSetup.tearDown(self)

    def remove_initfile(self):
        if isfile(self.initfile):
            os.remove(self.initfile)

    def test_no_initfile(self):
        self.assertEqual(isfile(self.initfile), False)

    def test_read_init_file_raises_exception(self):
        self.assertRaises(IOError, completer.read_init_file, 'my_init')

    def test_read_None_name(self):
        self.mkfile('my_init')
        self.mkfile(self.initfile)
        completer.read_init_file(None)

    def test_read_empty_string(self):
        self.mkfile('my_init')
        self.mkfile(self.initfile)
        completer.read_init_file('')

    def test_read_relative(self):
        self.mkfile('my_init')
        completer.read_init_file('my_init')

    def test_read_abspath(self):
        self.mkfile('my_init')
        completer.read_init_file(abspath('my_init'))

    def test_read_tilde_expanded(self):
        self.mkfile(self.initfile)
        completer.read_init_file('~/.$$$')

    if sys.version_info[0] >= 3:

        def test_read_bytes_name(self):
            self.mkfile(bytes('my_init', sys.getfilesystemencoding()))
            completer.read_init_file(bytes('my_init', sys.getfilesystemencoding()))


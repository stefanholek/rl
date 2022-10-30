"""Test helpers."""

import unittest
import os
import tempfile
import shutil

from os.path import realpath, isdir

from rl import completer
from rl import completion
from rl import history


def reset():
    completer.reset()
    completion.reset()
    history.reset()
    # Disable colors if enabled in ~/.inputrc
    completer.parse_and_bind('set colored-stats off')
    completer.parse_and_bind('set colored-completion-prefix off')
    completer.parse_and_bind('set enable-active-region off')


class JailSetup(unittest.TestCase):

    origdir = None
    tempdir = None

    def setUp(self):
        self.origdir = os.getcwd()
        self.tempdir = realpath(tempfile.mkdtemp())
        os.chdir(self.tempdir)

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.origdir is not None:
            if isdir(self.origdir):
                os.chdir(self.origdir)
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)

    def mkdir(self, *names):
        for name in names:
            os.mkdir(name)

    def mkfile(self, *names):
        for name in names:
            f = open(name, 'wt')
            f.write('\n')
            f.close()


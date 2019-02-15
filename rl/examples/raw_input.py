# Complete system commands

from __future__ import print_function
from six.moves import input

import os

from rl import completer
from rl import print_exc


class CompleteCommand(object):
    # A completion entry "function" implementing readline's
    # generator protocol

    @print_exc
    def __call__(self, text, state):
        if state == 0:
            self.matches = []
            # Find executables matching 'text'
            for dir in os.environ.get('PATH').split(':'):
                dir = os.path.expanduser(dir)
                if os.path.isdir(dir):
                    for name in os.listdir(dir):
                        if name.startswith(text):
                            if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                                self.matches.append(name)
        try:
            return self.matches[state]
        except IndexError:
            return None


def main():
    # Set the completion entry function
    completer.completer = CompleteCommand()

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    command = input('command> ')
    print('You typed:', command)


if __name__ == '__main__':
    main()

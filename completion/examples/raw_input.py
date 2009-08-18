# Complete system commands

import os

from completion import completer
from completion import generator


def completesys(text):
    matches = []
    for dir in os.environ.get('PATH').split(':'):
        for name in os.listdir(dir):
            if name.startswith(text):
                if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                    matches.append(name)
    return matches


def main():
    completer.parse_and_bind('TAB: complete')
    completer.completer = generator(completesys)
    command = raw_input('command> ')
    print 'You typed:', command


if __name__ == '__main__':
    main()
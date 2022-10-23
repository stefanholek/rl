# Complete system commands

import os

from rl import completer
from rl import generator
from rl import print_exc


@print_exc
@generator
def complete_command(text):
    # Return executables matching 'text'
    for dir in os.environ.get('PATH').split(':'):
        if os.path.isdir(dir):
            for name in os.listdir(dir):
                if name.startswith(text):
                    if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                        yield name


def main():
    # Set the completion entry function
    completer.completer = complete_command

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    command = input('command> ')
    print('You typed:', command)


if __name__ == '__main__':
    main()

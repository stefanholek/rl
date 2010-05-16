# Complete system commands

# Instead of implementing the generator protocol directly,
# we can provide a matcher function and use the generator
# factory on it.

import os
from rl import completer
from rl import generator
from rl import print_exc


@print_exc
def complete_command(text):
    # Return executables matching 'text'
    for dir in os.environ.get('PATH').split(':'):
        dir = os.path.expanduser(dir)
        if os.path.isdir(dir):
            for name in os.listdir(dir):
                if name.startswith(text):
                    if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                        yield name


def main():
    # Set the completion function
    completer.completer = generator(complete_command)

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    command = raw_input('command> ')
    print 'You typed:', command


if __name__ == '__main__':
    main()

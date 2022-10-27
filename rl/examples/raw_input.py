# Complete system commands

import os

from rl import completer


class CommandCompleter:
    # A completion entry function implementing readline's
    # generator protocol

    def __call__(self, text, state):
        if state == 0:
            self.matches = list(self.complete_command(text))
        try:
            return self.matches[state]
        except IndexError:
            return None

    def complete_command(self, text):
        # Return executables matching 'text'
        for dir in os.environ.get('PATH').split(':'):
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            yield name


def main():
    # Set the completion entry function
    completer.completer = CommandCompleter()

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    command = input('command> ')
    print('You typed:', command)


if __name__ == '__main__':
    main()

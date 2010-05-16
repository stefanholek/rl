# Complete system commands and filenames on the same line

# The cmd.Cmd class installs its own dispatcher to invoke completion
# functions defined by subclasses. It also enables TAB completion for us.

import os
import cmd

from rl import completer
from rl import completion


class SimpleApp(cmd.Cmd):

    intro = 'Completion example (type Ctrl+D to exit)\n'
    prompt = 'simpleapp> '

    def preloop(self):
        # Characters used to quote substrings
        completer.quote_characters = '\'"'
        # Characters used to find word boundaries
        completer.word_break_characters = '! \t\n"\'><=;|&(:'
        # Characters that trigger filename quoting
        completer.filename_quote_characters = '\\ \t\n"\'><=;|&()@#$`?*[!:{'

    def emptyline(self):
        pass

    def do_EOF(self, args):
        """Usage: Ctrl+D"""
        self.stdout.write('\n')
        return True

    def do_shell(self, args):
        """Usage: !command [filename ...]"""
        os.system(args)

    def complete_shell(self, text, line, begidx, endidx):
        # This function is called when the simpleapp command line
        # starts with an exclamation mark. It further dispatches
        # to filename completion or command completion, depending
        # on format and position of the completion word.
        matches = []
        if text.startswith('~') and (os.sep not in text):
            matches = completion.complete_username(text)
            if not matches:
                matches = completion.complete_filename(text)
        else:
            if self._is_command_pos(line, begidx) and (os.sep not in text):
                matches = self._complete_command(text)
            else:
                matches = completion.complete_filename(text)
        return matches

    def _is_command_pos(self, line, begidx):
        # Return True if we are completing a command name
        delta = line[0:begidx]
        return delta.strip() in ('!', 'shell')

    def _complete_command(self, text):
        # Return executables matching 'text'
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            yield name


def main():
    app = SimpleApp()
    app.cmdloop()


if __name__ == '__main__':
    main()

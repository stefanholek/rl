# Complete system commands and filenames on the same line

import os
import cmd

from rl import completer
from rl import completion


class MyCmd(cmd.Cmd):

    intro = 'Completion example (type Ctrl+D to exit)\n'
    prompt = 'command> '

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
        # Select the completion type depending on position
        # and format of the word being completed
        if text.startswith('~') and (os.sep not in text):
            return completion.complete_username(text)

        if self.commandpos(line, begidx) and (os.sep not in text):
            return self._complete_command(text)

        return completion.complete_filename(text)

    def commandpos(self, line, begidx):
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
    c = MyCmd()
    c.cmdloop()


if __name__ == '__main__':
    main()

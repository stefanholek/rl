# Complete system commands and filenames

import sys
import os

from completion import completer
from completion import completion
from completion import cmd


class MyCmd(cmd.Cmd):

    intro = 'completefiles example (type help for help)\n'
    prompt = 'completefiles> '

    def preloop(self):
        completer.quote_characters = '"\''
        completer.word_break_characters = ' \t\n\\"\'`><=;|&!?*'
        completer.filename_quote_characters = ' \t\n'
        completer.match_hidden_files = False
        completer.tilde_expansion = True

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
        if self.commandpos(line, begidx):
            if os.sep not in text:
                return self.completesys(text)
        return self.completefiles(text)

    def commandpos(self, line, begidx):
        delta = line[0:begidx]
        return delta.strip() in ('!', 'shell')

    def completesys(self, text):
        matches = []
        for dir in os.environ.get('PATH').split(':'):
            for name in os.listdir(dir):
                if name.startswith(text):
                    if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                        matches.append(name)
        return matches

    def completefiles(self, text):
        if text.startswith('~') and os.sep not in text:
            return completion.complete_username(text)
        return completion.complete_filename(text)


def main():
    c = MyCmd()
    c.cmdloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())


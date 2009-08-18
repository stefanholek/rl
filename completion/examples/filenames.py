# Complete filenames

import os

from completion import completer
from completion import completion
from completion import cmd


class MyCmd(cmd.Cmd):

    intro = 'Filename completion example (type Ctrl+D to exit)\n'
    prompt = 'filename> '

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

    def completenames(self, text, *ignored):
        if text.startswith('~') and os.sep not in text:
            return completion.username_completion_function(text)
        return completion.filename_completion_function(text)


def main():
    c = MyCmd()
    c.cmdloop()


if __name__ == '__main__':
    main()

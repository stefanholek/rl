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
        # Configure the completer for filename completion
        completer.quote_characters = '"\''
        completer.word_break_characters = '! \t\n"\'><=;|&(:'
        completer.filename_quote_characters = '\\ \t\n"\'><=;|&()@#$`?*[!:{'

    def emptyline(self):
        # Do nothing
        pass

    def do_EOF(self, args):
        """Usage: Ctrl+D"""
        self.stdout.write('\n')
        return True

    def do_shell(self, args):
        """Usage: !<command> [<filename> ...]"""
        os.system(args)

    def complete_shell(self, text, line, begidx, endidx):
        # This function is called when the command line starts
        # with an exclamation mark. It further dispatches to
        # filename completion or command completion, depending
        # on the format and position of the completion word.
        if line[0:begidx].strip() in ('!', 'shell'):
            if not text.startswith('~') and (os.sep not in text):
                return self.completecommand(text)
        return self.completefilename(text)

    def completefilename(self, text):
        # Return files and directories matching 'text'
        matches = []
        if text.startswith('~') and os.sep not in text:
            matches = completion.complete_username(text)
        if not matches:
            matches = completion.complete_filename(text)
        return matches

    def completecommand(self, text):
        # Return executables matching 'text'
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            yield name


def main():
    SimpleApp().cmdloop()


if __name__ == '__main__':
    main()

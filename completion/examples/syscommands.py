# Complete system commands

import sys
import os

from completion import cmd


class MyCmd(cmd.Cmd):

    intro = 'Command completion example (type help for help)\n'
    prompt = 'completion> '

    def emptyline(self):
        pass

    def do_EOF(self, args):
        """Usage: Ctrl+D"""
        self.stdout.write('\n')
        return True

    def do_shell(self, args):
        """Usage: !command"""
        os.system(args)

    def complete_shell(self, text, *ignored):
        return self.commandcomplete(text)

    def commandcomplete(self, text):
        matches = []
        for dir in os.environ.get('PATH').split(':'):
            for name in os.listdir(dir):
                if name.startswith(text):
                    if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                        matches.append(name)
        return matches


def main():
    c = MyCmd()
    c.cmdloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())


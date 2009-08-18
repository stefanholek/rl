# Complete system commands

import os

from completion import cmd


class MyCmd(cmd.Cmd):

    intro = 'Command completion example (type Ctrl+D to exit)\n'
    prompt = 'command> '

    def emptyline(self):
        pass

    def do_EOF(self, args):
        """Usage: Ctrl+D"""
        self.stdout.write('\n')
        return True

    def completenames(self, text, *ignored):
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


if __name__ == '__main__':
    main()


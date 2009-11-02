"""Importing this module modifies cmd.Cmd to use rl instead of readline."""

import cmd

from rl import completer
from rl import completion


def cmdloop(self, intro=None):
    """Repeatedly issue a prompt, accept input, parse an initial prefix
    off the received input, and dispatch to action methods, passing them
    the remainder of the line as argument. Uses rl.completer.
    """
    self.preloop()
    if self.use_rawinput and self.completekey:
        self.old_completer = completer.completer
        completer.completer = self.complete
        completer.parse_and_bind(self.completekey+": complete")
    try:
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro)+"\n")
        stop = None
        while not stop:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                if self.use_rawinput:
                    try:
                        line = raw_input(self.prompt)
                    except EOFError:
                        line = 'EOF'
                else:
                    self.stdout.write(self.prompt)
                    self.stdout.flush()
                    line = self.stdin.readline()
                    if not len(line):
                        line = 'EOF'
                    else:
                        line = line[:-1] # chop \n
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()
    finally:
        if self.use_rawinput and self.completekey:
            completer.completer = self.old_completer


def complete(self, text, state):
    """Return the next possible completion for 'text'.

    If a command has not been entered, then complete against command list.
    Otherwise try to call complete_<command> to get list of completions.
    Uses rl.completion.
    """
    if state == 0:
        origline = completion.line_buffer
        line = origline.lstrip()
        stripped = len(origline) - len(line)
        begidx = completion.begidx - stripped
        endidx = completion.endidx - stripped
        if begidx>0:
            cmd, args, foo = self.parseline(line)
            if cmd == '':
                compfunc = self.completedefault
            else:
                try:
                    compfunc = getattr(self, 'complete_' + cmd)
                except AttributeError:
                    compfunc = self.completedefault
        else:
            compfunc = self.completenames
        self.completion_matches = iter(compfunc(text, line, begidx, endidx))
    try:
        return self.completion_matches.next()
    except StopIteration:
        return None


# Monkey patch cmd.Cmd
cmd.Cmd.cmdloop = cmdloop
cmd.Cmd.complete = complete


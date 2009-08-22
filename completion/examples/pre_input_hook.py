# Show a pre-input hook at work

import os
from completion import completer
from completion import readline


lead_ins = (
    'My job is',
    'My hobby is',
    'When I was a kid, I always wanted to be a',
)

defaults = (
    'awesome!',
    'providing the balance I need',
    'fireman',
)

step = 0


def pre_input_hook():
    # The pre-input hook is used to insert text into
    # the line buffer that the user may then edit.
    readline.insert_text(defaults[step])
    readline.redisplay()


def main():
    global step

    # Set the pre-input hook
    completer.pre_input_hook = pre_input_hook

    print 'Please finish the following sentences:'
    print '--------------------------------------'

    # The prompt area is used for the text the user may
    # not overwrite or change.
    for step in range(len(lead_ins)):
        raw_input(lead_ins[step] + ': ')

    print 'Thank you!'


if __name__ == '__main__':
    main()

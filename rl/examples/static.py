# Complete from a static list of strings

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc

strings = ['foo-', 'bar-', 'baz+', 'peng+']


@print_exc
def complete(text):
    completion.suppress_append = True
    return [x for x in strings if x.startswith(text)]


def main():
    # Set the completion function
    completer.completer = generator(complete)

    # Enable TAB completion
    completer.parse_and_bind('tab: complete')

    line = raw_input('> ')
    print 'You typed:', line


if __name__ == '__main__':
    main()

# Complete from a static list of strings

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc

strings = ['foo-', 'bar-', 'baz+', 'peng+']


@print_exc
def complete_string(text):
    completion.suppress_append = True
    return [x for x in strings if x.startswith(text)]


def main():
    # Set the completion function
    completer.completer = generator(complete_string)

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    line = raw_input('string> ')
    print 'You typed:', line.strip()


if __name__ == '__main__':
    main()

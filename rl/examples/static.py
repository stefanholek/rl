# Complete from a static list of strings

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc

strings = ['foo-', 'bar-', 'baz+', 'peng+']


@print_exc
@generator
def complete_string(text):
    completion.suppress_append = True
    return [x for x in strings if x.startswith(text)]


def main():
    # Set the completion entry function
    completer.completer = complete_string

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    string = input('string> ')
    print('You typed:', string)


if __name__ == '__main__':
    main()

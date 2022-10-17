# Complete email addresses

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc

from rl.utils import DEFAULT_DELIMS


def complete_hostname(text):
    # Search /etc/hosts for matching hostnames
    with open('/etc/hosts', 'rt') as f:
        lines = f.readlines()
    for line in lines:
        line = line.split()
        if line and not line[0].startswith('#'):
            for hostname in line[1:]:
                if hostname.startswith(text[1:]):
                    yield '@' + hostname


@print_exc
@generator
def complete_email(text):
    # Dispatch to username or hostname completion
    if text.startswith('@'):
        return complete_hostname(text)
    else:
        completion.append_character = '@'
        return completion.complete_username(text)


def main():
    # Configure word break characters
    completer.word_break_characters = DEFAULT_DELIMS.replace('-', '')

    # Configure special prefixes
    completer.special_prefixes = '@'

    # Set the completion entry function
    completer.completer = complete_email

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    email = input('email> ')
    print('You typed:', email)


if __name__ == '__main__':
   main()

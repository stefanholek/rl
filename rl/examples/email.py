# Complete email addresses

# The completion function oftentimes is a dispatcher,
# forwarding calls to more specific completion functions.

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc


def complete_hostname(text):
    # Search /etc/hosts for matching hostnames
    f = open('/etc/hosts', 'rt')
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.split()
        if line and not line[0].startswith('#'):
            for hostname in line[1:]:
                if hostname.startswith(text[1:]):
                    yield '@' + hostname


@print_exc
def complete_email(text):
    # Dispatch to username or hostname completion
    if text.startswith('@'):
        return complete_hostname(text)
    else:
        completion.append_character = '@'
        return completion.complete_username(text)


def main():
    from rl.utils import DEFAULT_DELIMS

    # Configure word break characters
    completer.word_break_characters = DEFAULT_DELIMS.replace('-', '')

    # Configure special prefixes
    completer.special_prefixes = '@'

    # Set the completion function
    completer.completer = generator(complete_email)

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    try:
        email = raw_input('email> ')
    except (EOFError, KeyboardInterrupt):
        print # Newline
    else:
        print 'You typed:', email.strip()


if __name__ == '__main__':
   main()

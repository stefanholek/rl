# Complete email addresses

# In real life, the completion function oftentimes is a dispatcher,
# forwarding calls to more specific matcher functions.

from rl import completer
from rl import completion
from rl import generator


def complete_email(text):
    # Dispatch to username or hostname completion
    if not text.startswith('@'):
        completion.append_character = '@'
        return completion.complete_username(text)
    else:
        return complete_hostname(text)


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


def main():
    # Configure special prefixes
    completer.special_prefixes = '@'

    # Set the completion function
    completer.completer = generator(complete_email)

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    email = raw_input('email> ')
    print 'You typed:', email.strip()


if __name__ == '__main__':
    main()

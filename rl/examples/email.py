# Complete email addresses

from rl import completer
from rl import completion
from rl import generator


def complete(text):
    # We receive the '@' as part of the word
    if text.startswith('@'):
        return complete_hostname(text)
    else:
        completion.append_character = '@'
        return completion.complete_username(text)


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
    completer.completer = generator(complete)

    # Enable TAB completion
    completer.parse_and_bind('tab: complete')

    email = raw_input('email address: ')
    print 'Your email is:', email.strip()


if __name__ == '__main__':
    main()

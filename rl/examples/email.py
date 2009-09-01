# Complete email addresses

from rl import completer
from rl import completion
from rl import generator


def complete(text):
    # We receive the '@' as part of the word
    if not text.startswith('@'):
        completion.append_character = '@'
        return completion.complete_username(text)
    else:
        return complete_hostname(text)


def complete_hostname(text):
    # Hostnames must appear in /etc/hosts
    f = open('/etc/hosts', 'rt')
    hosts = f.read().strip()
    f.close()
    for line in hosts.split('\n'):
        line = filter(None, line.split())
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

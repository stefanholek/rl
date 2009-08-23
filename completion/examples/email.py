# Complete email addresses

from completion import completer
from completion import completion
from completion import generator


def complete(text):
    # '@' is a special prefix and we receive it as part
    # of the word. Hence, words starting with '@' are
    # hostnames and other words are usernames.
    if text.startswith('@'):
        return complete_hostname(text[1:])
    else:
        completion.append_character = '@'
        return completion.complete_username(text)


def complete_hostname(text):
    # To be offered for completion, hostnames must appear
    # in /etc/hosts.
    f = open('/etc/hosts', 'rt')
    hosts = f.read().strip()
    f.close()
    for line in hosts.split('\n'):
        line = filter(None, line.split())
        if line and not line[0].startswith('#'):
            for hostname in line[1:]:
                if hostname.startswith(text):
                    yield '@' + hostname


def main():
    # Configure special prefixes
    completer.special_prefixes = '@'

    # Configure the completion function
    completer.completer = generator(complete)

    # Enable TAB completion
    completer.parse_and_bind('tab: complete')

    email = raw_input('email address: ')
    print 'Your email is:', email.strip()


if __name__ == '__main__':
    main()

# Complete email addresses

from completion import completer
from completion import completion
from completion import generator


def completeemails(text):
    # If there is no '@' before word, complete usernames
    if completion.line_buffer.find('@', 0, completion.begidx) < 0:
        completion.append_character = '@'
        return completion.complete_username(text)
    # Else, complete hostnames
    return completehostnames(text)


def completehostnames(text):
    # To be offered for completion, hostnames must appear
    # in /etc/hosts
    f = open('/etc/hosts', 'rt')
    hosts = f.read().strip()
    f.close()
    for line in hosts.split('\n'):
        line = filter(None, line.split())
        if line and not line[0].startswith('#'):
            for hostname in line[1:]:
                if hostname.startswith(text):
                    yield hostname


def main():
    completer.completer = generator(completeemails)
    completer.parse_and_bind('tab: complete')
    address = raw_input('email address: ')
    print 'Your email is:', address.strip()


if __name__ == '__main__':
    main()

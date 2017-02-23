# Example display matches hook

from rl import completer
from rl import completion
from rl import readline


def display_matches_hook(substitution, matches, max_length):
    # Python implementation of the default display_matches_hook
    num_matches = len(matches)
    if num_matches >= completer.query_items > 0:
        sys.stdout.write('\nDisplay all %d possibilities? (y or n)' % num_matches)
        sys.stdout.flush()
        while True:
            c = readline.read_key()
            if c in 'yY\x20': # SPACEBAR
                break
            if c in 'nN\x7f': # RUBOUT
                sys.stdout.write('\n')
                completion.redisplay(force=True)
                return
    completion.display_match_list(substitution, matches, max_length)
    completion.redisplay(force=True)


# Example pre-input hook

from rl import completer
from rl import completion
from rl import print_exc


class Questionnaire(object):

    questions = ('My job is', 'My hobby is', 'I have always wanted to be a')
    defaults = ('great', 'golf', 'fireman')

    def __init__(self):
        completer.pre_input_hook = self.pre_input_hook

    def interact(self):
        # The prompt area is used for text the user
        # must not overwrite or change
        print('Please finish the following statements')
        print('--------------------------------------')
        for self.index in range(len(self.questions)):
            input(self.questions[self.index]+': ')
        print('Thank you!')

    @print_exc
    def pre_input_hook(self):
        # The pre-input hook is used to insert text into
        # the line buffer which the user may then edit
        completion.line_buffer = self.defaults[self.index]
        completion.redisplay()


def main():
    try:
        Questionnaire().interact()
    except (EOFError, KeyboardInterrupt):
        print() # Newline


if __name__ == '__main__':
    main()

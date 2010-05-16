# Show a pre-input hook at work

from rl import completer
from rl import completion


class Questionnaire(object):

    questions = ('My job is', 'My hobby is', 'I have always wanted to be a')
    defaults = ('great', 'golf', 'fireman')

    def __init__(self):
        completer.pre_input_hook = self.pre_input_hook

    def interact(self):
        print 'Please finish the following statements'
        print '--------------------------------------'
        # The prompt area is used for text the user
        # must not overwrite or change
        for self.index in range(len(self.questions)):
            raw_input(self.questions[self.index]+': ')
        print 'Thank you!'

    def pre_input_hook(self):
        # The pre-input hook is used to insert text into
        # the line buffer which the user may then edit
        completion.line_buffer = self.defaults[self.index]
        completion.redisplay()


def main():
    Questionnaire().interact()


if __name__ == '__main__':
    main()

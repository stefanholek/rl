# Show a pre-input hook at work

from rl import completer
from rl import completion


class Questionnaire(object):

    prompts = ('My job is', 'My hobby is', 'I have always wanted to be a')
    defaults = ('great', 'golf', 'fireman')

    def __init__(self):
        completer.pre_input_hook = self.pre_input_hook

    def interact(self):
        print 'Please finish the following statements'
        print '--------------------------------------'
        # The prompt area is used for text the user
        # must not overwrite or change
        for self.step in range(len(self.prompts)):
            raw_input(self.prompts[self.step]+': ')
        print 'Thank you!'

    def pre_input_hook(self):
        # The pre-input hook is used to insert text into
        # the line buffer which the user may then edit
        completion.line_buffer = self.defaults[self.step]
        completion.redisplay()


def main():
    Questionnaire().interact()


if __name__ == '__main__':
    main()

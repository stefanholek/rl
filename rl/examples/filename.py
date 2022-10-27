# Complete filenames

import sys
import unicodedata

from rl import completer
from rl import completion
from rl import generator
from rl import print_exc


@print_exc
def char_is_quoted(text, index):
    # Return True if the character at index is quoted
    return index > 0 and text[index-1] == '\\'


@print_exc
def quote_filename(text, single_match, quote_char):
    # Backslash-quote characters in text
    if quote_char == "'":
        pass
    elif quote_char == '"':
        for c in '\\"$`':
            text = text.replace(c, '\\'+c)
    else:
        for c in completer.filename_quote_characters:
            text = text.replace(c, '\\'+c)
    return text


@print_exc
def dequote_filename(text, quote_char):
    # Backslash-dequote characters in text
    if quote_char == "'":
        pass
    elif quote_char == '"':
        for c in '\\"$`':
            text = text.replace('\\'+c, c)
    else:
        for c in completer.filename_quote_characters:
            text = text.replace('\\'+c, c)
    return text


@print_exc
def rewrite_filename(text):
    # Normalize decomposed UTF-8 received from HFS Plus
    return unicodedata.normalize('NFC', text)


@print_exc
@generator
def complete_filename(text):
    matches = []
    # Complete usernames
    if text.startswith('~') and '/' not in text:
        matches = completion.complete_username(text)
    # Complete filenames
    if not matches:
        matches = completion.complete_filename(text)
    return matches


def main():
    # Configure quote characters
    completer.quote_characters = '\'"'
    completer.word_break_characters = ' \t\n"\'><;|&=(:'
    completer.filename_quote_characters = '\\ \t\n"\'@><;|&=()#$`?*[!:{'

    # Configure quoting functions
    completer.char_is_quoted_function = char_is_quoted
    completer.filename_quoting_function = quote_filename
    completer.filename_dequoting_function = dequote_filename

    # Configure Unicode converter on Mac OS X
    if sys.platform == "darwin":
        completer.filename_rewrite_hook = rewrite_filename

    # Set the completion entry function
    completer.completer = complete_filename

    # Enable TAB completion
    completer.parse_and_bind('TAB: complete')

    filename = input('file> ')
    print('You typed:', filename)


if __name__ == '__main__':
    main()

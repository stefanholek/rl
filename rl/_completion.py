"""Interface to the active readline completion."""

import sys
import _readline as readline


class Completion(object):
    """Interface to the active readline completion.

    This class is not intended for instantiation beyond
    the one ``completion`` object in this module.
    Applications wanting to use the Completion interface will
    typically import the ``completion`` object and use its
    properties and methods to implement custom completers.

    Example::

        from rl import completion

        def complete(text):
            completion.append_character = '@'
            return completion.complete_username(text)
    """

    MAX_MATCHES = 100000 # Just in case

    @property
    def begidx(self):
        """The start index of the word in the line."""
        return readline.get_begidx()

    @property
    def endidx(self):
        """The end index of the word in the line."""
        return readline.get_endidx()

    @property
    def completion_type(self):
        """The type of completion readline performs."""
        return readline.get_completion_type()

    @property
    def invoking_key(self):
        """The last character in the key sequence that invoked the
        completion."""
        return readline.get_completion_invoking_key()

    @property
    def found_quote(self):
        """True if the word contains or is delimited by a quote
        character."""
        return readline.get_completion_found_quote()

    @property
    def quote_character(self):
        """The quote character found."""
        return readline.get_completion_quote_character()

    @property
    def rl_point(self):
        """The position of the cursor in the line."""
        return readline.get_rl_point()

    @property
    def rl_end(self):
        """The last position in the line. The cursor range
        is defined as: ``0 <= rl_point <= rl_end``."""
        return readline.get_rl_end()

    @apply
    def line_buffer():
        doc="""The line buffer readline uses."""
        def get(self):
            return readline.get_line_buffer()
        def set(self, string):
            readline.replace_line(string)
        return property(get, set, doc=doc)

    @apply
    def append_character():
        doc="""The character appended when the completion returns a
        single match. Defaults to the space character."""
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            readline.set_completion_append_character(string)
        return property(get, set, doc=doc)

    @apply
    def suppress_append():
        doc="""Suppress the append character for this completion.
        Defaults to False."""
        def get(self):
            return readline.get_completion_suppress_append()
        def set(self, bool):
            readline.set_completion_suppress_append(bool)
        return property(get, set, doc=doc)

    @apply
    def suppress_quote():
        doc="""Do not append a matching quote character when performing
        completion on a quoted string. Defaults to False."""
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, bool):
            readline.set_completion_suppress_quote(bool)
        return property(get, set, doc=doc)

    @apply
    def attempted_completion_over():
        doc="""Do not fall back to the default filename completion,
        even if the current completion returns no matches.
        Defaults to True."""
        def get(self):
            return readline.get_attempted_completion_over()
        def set(self, bool):
            readline.set_attempted_completion_over(bool)
        return property(get, set, doc=doc)

    @apply
    def filename_completion_desired():
        doc="""Treat the results of matches as filenames.
        Directory names will have a slash appended, for example.
        Defaults to False."""
        def get(self):
            return readline.get_filename_completion_desired()
        def set(self, bool):
            readline.set_filename_completion_desired(bool)
        return property(get, set, doc=doc)

    @apply
    def filename_quoting_desired():
        doc="""Quote results according to filename quoting rules.
        Defaults to True."""
        def get(self):
            return readline.get_filename_quoting_desired()
        def set(self, bool):
            readline.set_filename_quoting_desired(bool)
        return property(get, set, doc=doc)

    @apply
    def sort_matches():
        doc="""Sort the list of completions. Defaults to True."""
        def get(self):
            return readline.get_sort_completion_matches()
        def set(self, bool):
            readline.set_sort_completion_matches(bool)
        return property(get, set, doc=doc)

    @apply
    def ignore_duplicates():
        doc="""Remove duplicates from the list of completions.
        Defaults to True."""
        def get(self):
            return readline.get_ignore_completion_duplicates()
        def set(self, bool):
            readline.set_ignore_completion_duplicates(bool)
        return property(get, set, doc=doc)

    @apply
    def inhibit_completion():
        doc="""Insert the completion character like any other character.
        Defaults to False."""
        def get(self):
            return readline.get_inhibit_completion()
        def set(self, bool):
            readline.set_inhibit_completion(bool)
        return property(get, set, doc=doc)

    # Completion functions

    def complete_filename(self, text):
        """Built-in filename completion."""
        return self._generate(text, readline.filename_completion_function)

    def complete_username(self, text):
        """Built-in username completion."""
        return self._generate(text, readline.username_completion_function)

    def expand_tilde(self, text):
        """Built-in tilde expansion."""
        return readline.tilde_expand(text)

    def display_match_list(self, substitution, matches, longest_match_length):
        """Built-in matches display."""
        readline.display_match_list(substitution, matches, longest_match_length)

    def _generate(self, text, entry_func):
        """Extract a list of matches from a generator function."""
        new = []
        for i in range(self.MAX_MATCHES):
            n = entry_func(text, i)
            if n is not None:
                new.append(n)
            else:
                break
        return new

    # Debugging

    def _dump(self, stream=sys.stdout):
        """Dump properties to stream."""
        stream.write("""\
line_buffer:                    %r
begidx:                         %s
endidx:                         %s
completion_type:                %s (%r)
invoking_key:                   %r
append_character:               %r
suppress_append:                %s
found_quote:                    %s
quote_character:                %r
suppress_quote:                 %s
attempted_completion_over:      %s
filename_completion_desired:    %s
filename_quoting_desired:       %s
sort_matches:                   %s
ignore_duplicates:              %s
inhibit_completion:             %s
""" % (
completion.line_buffer,
completion.begidx,
completion.endidx,
completion.completion_type, chr(completion.completion_type),
completion.invoking_key,
completion.append_character,
completion.suppress_append,
completion.found_quote,
completion.quote_character,
completion.suppress_quote,
completion.attempted_completion_over,
completion.filename_completion_desired,
completion.filename_quoting_desired,
completion.sort_matches,
completion.ignore_duplicates,
completion.inhibit_completion,
))

completion = Completion()


/* This module makes GNU readline available to Python.  It has ideas
 * contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
 * Center.  The completer interface was inspired by Lele Gaifax.  More
 * recently, it was largely rewritten by Guido van Rossum.
 */

/* Standard definitions */
#include "Python.h"
#include <setjmp.h>
#include <signal.h>
#include <errno.h>
#include <sys/time.h>

#if defined(HAVE_SETLOCALE)
/* GNU readline() mistakenly sets the LC_CTYPE locale.
 * This is evil.  Only the user or the app's main() should do this!
 * We must save and restore the locale around the rl_initialize() call.
 */
#define SAVE_LOCALE
#include <locale.h>
#endif

#ifdef SAVE_LOCALE
#  define RESTORE_LOCALE(sl) { setlocale(LC_CTYPE, sl); free(sl); }
#else
#  define RESTORE_LOCALE(sl) 
#endif

/* GNU readline definitions */
#undef HAVE_CONFIG_H /* Else readline/chardefs.h includes strings.h */
#include <readline/readline.h>
#include <readline/history.h>

#ifdef HAVE_RL_COMPLETION_MATCHES
#define completion_matches(x, y) \
	rl_completion_matches((x), ((rl_compentry_func_t *)(y)))
#else
extern char **completion_matches(char *, rl_compentry_func_t *);
#endif

static void
on_completion_display_matches_hook(char **matches,
				   int num_matches, int max_length);


/* Exported function to send one line to readline's init file parser */

static PyObject *
parse_and_bind(PyObject *self, PyObject *args)
{
	char *s, *copy;
	if (!PyArg_ParseTuple(args, "s:parse_and_bind", &s))
		return NULL;
	/* Make a copy -- rl_parse_and_bind() modifies its argument */
	/* Bernard Herzog */
	copy = strdup(s);
	if (copy == NULL)
		return PyErr_NoMemory();
	rl_parse_and_bind(copy);
	free(copy); /* Free the copy */
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_parse_and_bind,
"parse_and_bind(string) -> None\n\
Parse and execute single line of a readline init file.");


/* Exported function to parse a readline init file */

static PyObject *
read_init_file(PyObject *self, PyObject *args)
{
	char *s = NULL;
	if (!PyArg_ParseTuple(args, "|z:read_init_file", &s))
		return NULL;
	errno = rl_read_init_file(s);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_read_init_file,
"read_init_file([filename]) -> None\n\
Parse a readline initialization file.\n\
The default filename is the last filename used.");


/* Exported function to load a readline history file */

static PyObject *
read_history_file(PyObject *self, PyObject *args)
{
	char *s = NULL;
	if (!PyArg_ParseTuple(args, "|z:read_history_file", &s))
		return NULL;
	errno = read_history(s);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

static int _history_length = -1; /* do not truncate history by default */
PyDoc_STRVAR(doc_read_history_file,
"read_history_file([filename]) -> None\n\
Load a readline history file.\n\
The default filename is ~/.history.");


/* Exported function to save a readline history file */

static PyObject *
write_history_file(PyObject *self, PyObject *args)
{
	char *s = NULL;
	if (!PyArg_ParseTuple(args, "|z:write_history_file", &s))
		return NULL;
	errno = write_history(s);
	if (!errno && _history_length >= 0)
		history_truncate_file(s, _history_length);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_write_history_file,
"write_history_file([filename]) -> None\n\
Save a readline history file.\n\
The default filename is ~/.history.");


/* Set history length */

static PyObject*
set_history_length(PyObject *self, PyObject *args)
{
	int length = _history_length;
	if (!PyArg_ParseTuple(args, "i:set_history_length", &length))
		return NULL;
	_history_length = length;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(set_history_length_doc,
"set_history_length(length) -> None\n\
Set the maximal number of items which will be written to\n\
the history file. A negative length is used to inhibit\n\
history truncation.");


/* Get history length */

static PyObject*
get_history_length(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(_history_length);
}

PyDoc_STRVAR(get_history_length_doc,
"get_history_length() -> int\n\
Return the maximum number of items that will be written to\n\
the history file.");


/* Generic hook function setter */

static PyObject *
set_hook(const char *funcname, PyObject **hook_var, PyObject *args)
{
	PyObject *function = Py_None;
	char buf[80];
	PyOS_snprintf(buf, sizeof(buf), "|O:set_%.50s", funcname);
	if (!PyArg_ParseTuple(args, buf, &function))
		return NULL;
	if (function == Py_None) {
		Py_XDECREF(*hook_var);
		*hook_var = NULL;
	}
	else if (PyCallable_Check(function)) {
		PyObject *tmp = *hook_var;
		Py_INCREF(function);
		*hook_var = function;
		Py_XDECREF(tmp);
	}
	else {
		PyOS_snprintf(buf, sizeof(buf),
			      "set_%.50s(func): argument not callable",
			      funcname);
		PyErr_SetString(PyExc_TypeError, buf);
		return NULL;
	}
	Py_RETURN_NONE;
}


/* Exported functions to specify hook functions in Python */

static PyObject *completion_display_matches_hook = NULL;
static PyObject *startup_hook = NULL;

#ifdef HAVE_RL_PRE_INPUT_HOOK
static PyObject *pre_input_hook = NULL;
#endif

static PyObject *
set_completion_display_matches_hook(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("completion_display_matches_hook",
			&completion_display_matches_hook, args);
#ifdef HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK
	/* We cannot set this hook globally, since it replaces the
	   default completion display. */
	rl_completion_display_matches_hook =
		completion_display_matches_hook ?
		(rl_compdisp_func_t *)on_completion_display_matches_hook : 0;
#endif
	return result;

}

PyDoc_STRVAR(doc_set_completion_display_matches_hook,
"set_completion_display_matches_hook([function]) -> None\n\
Set or remove the completion display function.\n\
The function is called as \
  ``function(substitution, matches, longest_match_length)`` \
once each time matches need to be displayed.");

static PyObject *
set_startup_hook(PyObject *self, PyObject *args)
{
	return set_hook("startup_hook", &startup_hook, args);
}

PyDoc_STRVAR(doc_set_startup_hook,
"set_startup_hook([function]) -> None\n\
Set or remove the startup_hook function.\n\
The function is called with no arguments just\n\
before readline prints the first prompt.");


#ifdef HAVE_RL_PRE_INPUT_HOOK

/* Set pre-input hook */

static PyObject *
set_pre_input_hook(PyObject *self, PyObject *args)
{
	return set_hook("pre_input_hook", &pre_input_hook, args);
}

PyDoc_STRVAR(doc_set_pre_input_hook,
"set_pre_input_hook([function]) -> None\n\
Set or remove the pre_input_hook function.\n\
The function is called with no arguments after the first prompt\n\
has been printed and just before readline starts reading input\n\
characters.");

#endif


/* Exported function to specify a word completer in Python */

static PyObject *completer = NULL;

static PyObject *begidx = NULL;
static PyObject *endidx = NULL;


/* Get the completion type for the scope of the tab-completion */
static PyObject *
get_completion_type(PyObject *self, PyObject *noarg)
{
	return PyString_FromFormat("%c", rl_completion_type);
}

PyDoc_STRVAR(doc_get_completion_type,
"get_completion_type() -> string\n\
Get the type of completion being attempted.");


/* Get the beginning index for the scope of the tab-completion */

static PyObject *
get_begidx(PyObject *self, PyObject *noarg)
{
	Py_INCREF(begidx);
	return begidx;
}

PyDoc_STRVAR(doc_get_begidx,
"get_begidx() -> int\n\
Get the beginning index of the readline tab-completion scope.");


/* Get the ending index for the scope of the tab-completion */

static PyObject *
get_endidx(PyObject *self, PyObject *noarg)
{
	Py_INCREF(endidx);
	return endidx;
}

PyDoc_STRVAR(doc_get_endidx,
"get_endidx() -> int\n\
Get the ending index of the readline tab-completion scope.");


/* Set the tab-completion word-delimiters that readline uses */

static PyObject *
set_completer_delims(PyObject *self, PyObject *args)
{
	char *break_chars;

	if(!PyArg_ParseTuple(args, "s:set_completer_delims", &break_chars)) {
		return NULL;
	}
	free((void*)rl_completer_word_break_characters);
	rl_completer_word_break_characters = strdup(break_chars);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completer_delims,
"set_completer_delims(string) -> None\n\
Set the readline word delimiters for tab-completion.");

static PyObject *
py_remove_history(PyObject *self, PyObject *args)
{
	int entry_number;
	HIST_ENTRY *entry;

	if (!PyArg_ParseTuple(args, "i:remove_history", &entry_number))
		return NULL;
	if (entry_number < 0) {
		PyErr_SetString(PyExc_ValueError,
				"History index cannot be negative");
		return NULL;
	}
	entry = remove_history(entry_number);
	if (!entry) {
		PyErr_Format(PyExc_ValueError,
			     "No history item at position %d",
			      entry_number);
		return NULL;
	}
	/* free memory allocated for the history entry */
	if (entry->line)
		free(entry->line);
	if (entry->data)
		free(entry->data);
	free(entry);

	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_remove_history,
"remove_history_item(pos) -> None\n\
Remove history item given by its position.");

static PyObject *
py_replace_history(PyObject *self, PyObject *args)
{
	int entry_number;
	char *line;
	HIST_ENTRY *old_entry;

	if (!PyArg_ParseTuple(args, "is:replace_history", &entry_number,
			      &line)) {
		return NULL;
	}
	if (entry_number < 0) {
		PyErr_SetString(PyExc_ValueError,
				"History index cannot be negative");
		return NULL;
	}
	old_entry = replace_history_entry(entry_number, line, (void *)NULL);
	if (!old_entry) {
		PyErr_Format(PyExc_ValueError,
			     "No history item at position %d",
			     entry_number);
		return NULL;
	}
	/* free memory allocated for the old history entry */
	if (old_entry->line)
	    free(old_entry->line);
	if (old_entry->data)
	    free(old_entry->data);
	free(old_entry);

	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_replace_history,
"replace_history_item(pos, line) -> None\n\
Replaces history item given by its position with contents of line.");

/* Add a line to the history buffer */

static PyObject *
py_add_history(PyObject *self, PyObject *args)
{
	char *line;

	if(!PyArg_ParseTuple(args, "s:add_history", &line)) {
		return NULL;
	}
	add_history(line);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_add_history,
"add_history(string) -> None\n\
Add a line to the history buffer.");


/* Get the tab-completion word-delimiters that readline uses */

static PyObject *
get_completer_delims(PyObject *self, PyObject *noarg)
{
	return PyString_FromString(rl_completer_word_break_characters);
}

PyDoc_STRVAR(doc_get_completer_delims,
"get_completer_delims() -> string\n\
Get the readline word delimiters for tab-completion.");


/* Set the completer function */

static PyObject *
set_completer(PyObject *self, PyObject *args)
{
	return set_hook("completer", &completer, args);
}

PyDoc_STRVAR(doc_set_completer,
"set_completer([function]) -> None\n\
Set or remove the completer function.\n\
The function is called as ``function(text, state)``,\n\
for state in 0, 1, 2, ..., until it returns a non-string.\n\
It should return the next possible completion starting with ``text``.");


static PyObject *
get_completer(PyObject *self, PyObject *noargs)
{
	if (completer == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(completer);
	return completer;
}

PyDoc_STRVAR(doc_get_completer,
"get_completer() -> function\n\
\n\
Returns current completer function.");

/* Exported function to get any element of history */

static PyObject *
get_history_item(PyObject *self, PyObject *args)
{
	int idx = 0;
	HIST_ENTRY *hist_ent;

	if (!PyArg_ParseTuple(args, "i:index", &idx))
		return NULL;
	if ((hist_ent = history_get(idx)))
		return PyString_FromString(hist_ent->line);
	else {
		Py_RETURN_NONE;
	}
}

PyDoc_STRVAR(doc_get_history_item,
"get_history_item(pos) -> string\n\
Return the current contents of history item at pos.");


/* Exported function to get current length of history */

static PyObject *
get_current_history_length(PyObject *self, PyObject *noarg)
{
	HISTORY_STATE *hist_st;

	hist_st = history_get_history_state();
	return PyInt_FromLong(hist_st ? (long) hist_st->length : (long) 0);
}

PyDoc_STRVAR(doc_get_current_history_length,
"get_current_history_length() -> int\n\
Return the current (not the maximum) length of history.");


/* Exported function to read the current line buffer */

static PyObject *
get_line_buffer(PyObject *self, PyObject *noarg)
{
	return PyString_FromString(rl_line_buffer);
}

PyDoc_STRVAR(doc_get_line_buffer,
"get_line_buffer() -> string\n\
Return the current contents of the line buffer.");


#ifdef HAVE_RL_COMPLETION_APPEND_CHARACTER

/* Exported function to clear the current history */

static PyObject *
py_clear_history(PyObject *self, PyObject *noarg)
{
	clear_history();
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_clear_history,
"clear_history() -> None\n\
Clear the current readline history.");
#endif


/* Exported function to insert text into the line buffer */

static PyObject *
insert_text(PyObject *self, PyObject *args)
{
	char *s;
	if (!PyArg_ParseTuple(args, "s:insert_text", &s))
		return NULL;
	rl_insert_text(s);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_insert_text,
"insert_text(string) -> None\n\
Insert text into the command line.");


/* Redisplay the line buffer */

extern int rl_display_fixed;

static PyObject *
redisplay(PyObject *self, PyObject *args)
{
	int force = 0;

	if (!PyArg_ParseTuple(args, "|i:redisplay", &force))
		return NULL;

	if (force) {
		rl_forced_update_display();
		rl_display_fixed = 1;
	}
	else {
		rl_redisplay();
	}

	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_redisplay,
"redisplay([force]) -> None\n\
Change what's displayed on the screen to reflect the current \
contents of the line buffer. If ``force`` is True, readline will \
refresh the display even if its internal state indicates \
an up-to-date screen.");


/* <_readline.c> */
/* http://tiswww.case.edu/php/chet/readline/readline.html#SEC44 */

#ifdef HAVE_RL_COMPLETION_APPEND_CHARACTER

/* Get/set completion append character */

static PyObject *
get_completion_append_character(PyObject *self, PyObject *noarg)
{
	if (!rl_completion_append_character)
		return PyString_FromStringAndSize(NULL, 0);

	return PyString_FromFormat("%c", rl_completion_append_character);
}

PyDoc_STRVAR(doc_get_completion_append_character,
"get_completion_append_character() -> string\n\
Get the character appended after the current completion.");


static PyObject *
set_completion_append_character(PyObject *self, PyObject *args)
{
	char *value;

	if (!PyArg_ParseTuple(args, "s:set_completion_append_character", &value)) {
		return NULL;
	}
	rl_completion_append_character = (value && *value) ? *value : '\0';
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_append_character,
"set_completion_append_character(string) -> None\n\
Set the character appended after the current completion. \
May only be called from within custom completers.");

#endif


/* Get/set completion suppress append */

static PyObject *
get_completion_suppress_append(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_completion_suppress_append);
}

PyDoc_STRVAR(doc_get_completion_suppress_append,
"get_completion_suppress_append() -> bool\n\
Do not append the completion_append_character after the current completion.");


static PyObject *
set_completion_suppress_append(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_completion_suppress_append", &value)) {
		return NULL;
	}
	rl_completion_suppress_append = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_suppress_append,
"set_completion_suppress_append(bool) -> None\n\
Do not append the completion_append_character after the current completion. \
May only be called from within custom completers.");


/* Get/set completer quote characters */

static PyObject *
get_completer_quote_characters(PyObject *self, PyObject *noarg)
{
	if (!rl_completer_quote_characters)
		return PyString_FromStringAndSize(NULL, 0);

	return PyString_FromString(rl_completer_quote_characters);
}

PyDoc_STRVAR(doc_get_completer_quote_characters,
"get_completer_quote_characters() -> string\n\
Get list of characters that may be used to quote a substring of the line.");


static PyObject *
set_completer_quote_characters(PyObject *self, PyObject *args)
{
	char *value;

	if (!PyArg_ParseTuple(args, "s:set_completer_quote_characters", &value)) {
		return NULL;
	}
	if (rl_completer_quote_characters)
		free((void*)rl_completer_quote_characters);
	rl_completer_quote_characters = strdup(value);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completer_quote_characters,
"set_completer_quote_characters(string) -> None\n\
Set list of characters that may be used to quote a substring of the line.");


/* Get/set filename quote characters */

static PyObject *
get_filename_quote_characters(PyObject *self, PyObject *noarg)
{
	if (!rl_filename_quote_characters)
		return PyString_FromStringAndSize(NULL, 0);

	return PyString_FromString(rl_filename_quote_characters);
}

PyDoc_STRVAR(doc_get_filename_quote_characters,
"get_filename_quote_characters() -> string\n\
Get list of characters that cause a filename to be quoted by the completer.");


static PyObject *
set_filename_quote_characters(PyObject *self, PyObject *args)
{
	char *value;

	if (!PyArg_ParseTuple(args, "s:set_filename_quote_characters", &value)) {
		return NULL;
	}
	if (rl_filename_quote_characters)
		free((void*)rl_filename_quote_characters);
	rl_filename_quote_characters = strdup(value);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_filename_quote_characters,
"set_filename_quote_characters(string) -> None\n\
Set list of characters that cause a filename to be quoted by the completer.");


/* Completion quoting */

static PyObject *
get_completion_found_quote(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_completion_found_quote);
}

PyDoc_STRVAR(doc_get_completion_found_quote,
"get_completion_found_quote() -> bool\n\
When readline is completing quoted text, it sets this variable to True \
if the word being completed contains any quoting character (including backslashes).");


static PyObject *
get_completion_quote_character(PyObject *self, PyObject *noarg)
{
	if (!rl_completion_quote_character)
		return PyString_FromStringAndSize(NULL, 0);

	return PyString_FromFormat("%c", rl_completion_quote_character);
}

PyDoc_STRVAR(doc_get_completion_quote_character,
"get_completion_quote_character() -> string\n\
When readline is completing quoted text, it sets this variable to the quoting character found.");


static PyObject *
get_completion_suppress_quote(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_completion_suppress_quote);
}

PyDoc_STRVAR(doc_get_completion_suppress_quote,
"get_completion_suppress_quote() -> bool\n\
Do not append a matching quote character when performing completion on a quoted string.");


static PyObject *
set_completion_suppress_quote(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_completion_suppress_quote", &value)) {
		return NULL;
	}
	rl_completion_suppress_quote = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_suppress_quote,
"set_completion_suppress_quote(bool) -> None\n\
Do not append a matching quote character when performing completion on a quoted string. \
May only be called from within custom completers.");


/* Filename completion flags */

static PyObject *
get_filename_completion_desired(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_filename_completion_desired);
}

PyDoc_STRVAR(doc_get_filename_completion_desired,
"get_filename_completion_desired() -> bool\n\
If True, treat the results of matches as filenames.");


static PyObject *
set_filename_completion_desired(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_filename_completion_desired", &value)) {
		return NULL;
	}
	rl_filename_completion_desired = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_filename_completion_desired,
"set_filename_completion_desired(bool) -> None\n\
If True, treat the results of matches as filenames. \
May only be called from within custom completers.");


static PyObject *
get_filename_quoting_desired(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_filename_quoting_desired);
}

PyDoc_STRVAR(doc_get_filename_quoting_desired,
"get_filename_quoting_desired() -> bool\n\
If True, filenames will be quoted.");


static PyObject *
set_filename_quoting_desired(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_filename_quoting_desired", &value)) {
		return NULL;
	}
	rl_filename_quoting_desired = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_filename_quoting_desired,
"set_filename_quoting_desired(bool) -> None\n\
If True, filenames will be quoted. \
May only be called from within custom completers.");


/*
static PyObject *
get_attempted_completion_over(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_attempted_completion_over);
}

PyDoc_STRVAR(doc_get_attempted_completion_over,
"get_attempted_completion_over() -> bool\n\
If True, do not fall back to the default filename completion, even if the current \
completion returns no matches.");


static PyObject *
set_attempted_completion_over(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_attempted_completion_over", &value)) {
		return NULL;
	}
	rl_attempted_completion_over = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_attempted_completion_over,
"set_attempted_completion_over(bool) -> None\n\
If True, do not fall back to the default filename completion, even if the current \
completion returns no matches. \
May only be called from within custom completers.");
*/


/* Misc flags */

/*
static PyObject *
get_sort_completion_matches(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_sort_completion_matches);
}

PyDoc_STRVAR(doc_get_sort_completion_matches,
"get_sort_completion_matches() -> bool\n\
If an application sets this variable to False, readline will not sort the list of completions.");


static PyObject *
set_sort_completion_matches(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_sort_completion_matches", &value)) {
		return NULL;
	}
	rl_sort_completion_matches = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_sort_completion_matches,
"set_sort_completion_matches(bool) -> None\n\
If an application sets this variable to False, readline will not sort the list of completions. \
May only be called from within custom completers.");


static PyObject *
get_ignore_completion_duplicates(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_ignore_completion_duplicates);
}

PyDoc_STRVAR(doc_get_ignore_completion_duplicates,
"get_ignore_completion_duplicates() -> bool\n\
If an application sets this variable to False, readline will not remove duplicates from the list of completions.");


static PyObject *
set_ignore_completion_duplicates(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_ignore_completion_duplicates", &value)) {
		return NULL;
	}
	rl_ignore_completion_duplicates = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_ignore_completion_duplicates,
"set_ignore_completion_duplicates(bool) -> None\n\
If an application sets this variable to False, readline will not remove duplicates from the list of completions. \
May only be called from within custom completers.");


static PyObject *
get_completion_mark_symlink_dirs(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_completion_mark_symlink_dirs);
}

PyDoc_STRVAR(doc_get_completion_mark_symlink_dirs,
"get_completion_mark_symlink_dirs() -> bool\n\
If True, a slash will be appended to completed filenames that are symbolic links to directory names.");


static PyObject *
set_completion_mark_symlink_dirs(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_completion_mark_symlink_dirs", &value)) {
		return NULL;
	}
	rl_completion_mark_symlink_dirs = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_mark_symlink_dirs,
"set_completion_mark_symlink_dirs(bool) -> None\n\
If True, a slash will be appended to completed filenames that are symbolic links to directory names. \
May only be called from within custom completers.");
*/


static PyObject *
get_inhibit_completion(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_inhibit_completion);
}

PyDoc_STRVAR(doc_get_inhibit_completion,
"get_inhibit_completion() -> bool\n\
If True, completion is disabled.");


static PyObject *
set_inhibit_completion(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_inhibit_completion", &value)) {
		return NULL;
	}
	rl_inhibit_completion = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_inhibit_completion,
"set_inhibit_completion(bool) -> None\n\
If True, completion is disabled. \
May only be called from within custom completers.");


/* Filename quoting/dequoting functions */

static PyObject *filename_quoting_function = NULL;
static rl_quote_func_t *default_filename_quoting_function = NULL;

static char *
on_filename_quoting_function(const char *text, int match_type, char *quote_pointer);


static PyObject *
set_filename_quoting_function(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("filename_quoting_function",
			&filename_quoting_function, args);

	rl_filename_quoting_function =
		filename_quoting_function ?
		(rl_quote_func_t *)on_filename_quoting_function :
		default_filename_quoting_function;

	return result;
}

PyDoc_STRVAR(doc_set_filename_quoting_function,
"set_filename_quoting_function([function]) -> None\n\
Set or remove the filename quoting function. \
The function is called as ``function(text, single_match, quote_char)`` \
and should return a string representing a quoted version of ``text``, \
or None to indicate no change. The ``single_match`` argument is True \
if the completion has generated only one match.");


static PyObject *
get_filename_quoting_function(PyObject *self, PyObject *noargs)
{
	if (filename_quoting_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(filename_quoting_function);
	return filename_quoting_function;
}

PyDoc_STRVAR(doc_get_filename_quoting_function,
"get_filename_quoting_function() -> function\n\
Get the current filename quoting function.");


static char *
on_filename_quoting_function(const char *text, int match_type, char *quote_pointer)
/* This function must return new memory on success and the
   passed-in 'text' pointer to indicate no change. */
{
	char *result = (char*)text;
	char *s = NULL;
	char quote_char_string[2] = "\0\0";
	PyObject *single_match = NULL;
	PyObject *r;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	single_match = PyBool_FromLong(match_type == SINGLE_MATCH);

	if (quote_pointer && *quote_pointer) {
		quote_char_string[0] = *quote_pointer;
	}

	r = PyObject_CallFunction(filename_quoting_function, "sOs",
				  text, single_match, quote_char_string);
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = (char*)text;
	}
	else {
		s = PyString_AsString(r);
		if (s == NULL)
			goto error;

		s = strdup(s);
		if (s != NULL)
			result = s;
	}
	Py_DECREF(single_match);
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(single_match);
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


static PyObject *filename_dequoting_function = NULL;

static char *
on_filename_dequoting_function(const char *text, char quote_char);


static PyObject *
set_filename_dequoting_function(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("filename_dequoting_function",
			&filename_dequoting_function, args);

	rl_filename_dequoting_function =
		filename_dequoting_function ?
		(rl_dequote_func_t *)on_filename_dequoting_function : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_filename_dequoting_function,
"set_filename_dequoting_function([function]) -> None\n\
Set or remove the filename dequoting function. \
The function is called as ``function(text, quote_char)`` \
and should return a string representing a dequoted version \
of ``text``, or None to indicate no change.");


static PyObject *
get_filename_dequoting_function(PyObject *self, PyObject *noargs)
{
	if (filename_dequoting_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(filename_dequoting_function);
	return filename_dequoting_function;
}

PyDoc_STRVAR(doc_get_filename_dequoting_function,
"get_filename_dequoting_function() -> function\n\
Get the current filename dequoting function.");


static char *
on_filename_dequoting_function(const char *text, char quote_char)
/* This function must always return new memory, which means
   at least a copy of 'text', and never NULL. */
{
	char *result = NULL;
	char *s = NULL;
	char quote_char_string[2] = "\0\0";
	PyObject *r;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	if (quote_char) {
		quote_char_string[0] = quote_char;
	}

	r = PyObject_CallFunction(filename_dequoting_function, "ss",
				  text, quote_char_string);
	if (r == NULL) {
		result = strdup(text);
		goto error;
	}
	if (r == Py_None) {
		result = strdup(text);
	}
	else {
		s = PyString_AsString(r);
		if (s == NULL) {
			result = strdup(text);
			goto error;
		}
		result = strdup(s);
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	/* We really can't return NULL here, so we abort like
	   readline's xmalloc. */
	if (result == NULL) {
		fprintf(stderr, "readline: out of virtual memory\n");
		exit(2);
	}
	return result;
}


static PyObject *char_is_quoted_function = NULL;

static int
on_char_is_quoted_function(const char *text, int index);


static PyObject *
set_char_is_quoted_function(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("char_is_quoted_function",
			&char_is_quoted_function, args);

	rl_char_is_quoted_p =
		char_is_quoted_function ?
		(rl_linebuf_func_t *)on_char_is_quoted_function : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_char_is_quoted_function,
"set_char_is_quoted_function([function]) -> None\n\
Set or remove the function that determines whether or not a \
specific character in the line buffer is quoted. \
The function is called as ``function(text, index)`` and should return \
True if the character at ``index`` is quoted, and False otherwise.");


static PyObject *
get_char_is_quoted_function(PyObject *self, PyObject *noargs)
{
	if (char_is_quoted_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(char_is_quoted_function);
	return char_is_quoted_function;
}

PyDoc_STRVAR(doc_get_char_is_quoted_function,
"get_char_is_quoted_function() -> function\n\
Get the function that determines whether or not a specific character \
in the line buffer is quoted.");


static int
on_char_is_quoted_function(const char *text, int index)
{
	int result = 0;
	int i = 0;
	PyObject *r;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	r = PyObject_CallFunction(char_is_quoted_function, "si", text, index);
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
		i = PyInt_AsLong(r);
		if (i == -1 && PyErr_Occurred())
			goto error;
		result = i;
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Stock completer functions */

static PyObject *
filename_completion_function(PyObject *self, PyObject *args)
{
	int state;
	char *value;
	char *completion;

	if (!PyArg_ParseTuple(args, "si:filename_completion_function", &value, &state)) {
		return NULL;
	}
	completion = rl_filename_completion_function(value, state);
	if (completion)
		/* We don't own the string so no freeing required */
		return PyString_FromString(completion);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_filename_completion_function,
"filename_completion_function(text, state) -> string\n\
A built-in generator function for filename completion.");


static PyObject *
username_completion_function(PyObject *self, PyObject *args)
{
	int state;
	char *value;
	char *completion;

	if (!PyArg_ParseTuple(args, "si:username_completion_function", &value, &state)) {
		return NULL;
	}
	completion = rl_username_completion_function(value, state);
	if (completion)
		/* We don't own the string so no freeing required */
		return PyString_FromString(completion);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_username_completion_function,
"username_completion_function(text, state) -> string\n\
A built-in generator function for username completion.");


static PyObject *
py_tilde_expand(PyObject *self, PyObject *args)
{
	char *value;
	char *expanded;
	PyObject *r;

	if (!PyArg_ParseTuple(args, "s:tilde_expand", &value)) {
		return NULL;
	}

	/* tilde_expand aborts on out of memory condition */
	expanded = tilde_expand(value);
	r = PyString_FromString(expanded);
	free(expanded);
	return r;
}

PyDoc_STRVAR(doc_tilde_expand,
"tilde_expand(string) -> string\n\
Return a new string which is the result of tilde expanding string.");


/* Special prefixes */

static PyObject *
get_special_prefixes(PyObject *self, PyObject *noarg)
{
	if (!rl_special_prefixes)
		return PyString_FromStringAndSize(NULL, 0);

	return PyString_FromString(rl_special_prefixes);
}

PyDoc_STRVAR(doc_get_special_prefixes,
"get_special_prefixes() -> string\n\
Characters that are word break characters, but should be left in text \
when it is passed to the completion function.");


static PyObject *
set_special_prefixes(PyObject *self, PyObject *args)
{
	char *value;

	if (!PyArg_ParseTuple(args, "s:set_special_prefixes", &value)) {
		return NULL;
	}
	if (rl_special_prefixes)
		free((void*)rl_special_prefixes);
	rl_special_prefixes = strdup(value);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_special_prefixes,
"set_special_prefixes(string) -> None\n\
Characters that are word break characters, but should be left in text \
when it is passed to the completion function.");


/* Query items */

static PyObject *
get_completion_query_items(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(rl_completion_query_items);
}

PyDoc_STRVAR(doc_get_completion_query_items,
"get_completion_query_items() -> int\n\
Up to this many items will be displayed in response to a possible-completions call.");


static PyObject *
set_completion_query_items(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_completion_query_items", &value)) {
		return NULL;
	}
	rl_completion_query_items = value;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_query_items,
"set_completion_query_items(int) -> None\n\
Up to this many items will be displayed in response to a possible-completions call.");


/* Invoking key */

/*
static PyObject *
get_completion_invoking_key(PyObject *self, PyObject *noarg)
{
	return PyString_FromFormat("%c", rl_completion_invoking_key);
}

PyDoc_STRVAR(doc_get_completion_invoking_key,
"get_completion_invoking_key() -> string\n\
The final character in the key sequence that invoked the completion function.");
*/


/* Missing APIs */

static PyObject *
get_completion_display_matches_hook(PyObject *self, PyObject *noargs)
{
	if (completion_display_matches_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(completion_display_matches_hook);
	return completion_display_matches_hook;
}

PyDoc_STRVAR(doc_get_completion_display_matches_hook,
"get_completion_display_matches_hook() -> function\n\
Get the current completion display function.");


static PyObject *
get_startup_hook(PyObject *self, PyObject *noargs)
{
	if (startup_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(startup_hook);
	return startup_hook;
}

PyDoc_STRVAR(doc_get_startup_hook,
"get_startup_hook() -> function\n\
Get the current startup_hook function.");


static PyObject *
get_pre_input_hook(PyObject *self, PyObject *noargs)
{
	if (pre_input_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(pre_input_hook);
	return pre_input_hook;
}

PyDoc_STRVAR(doc_get_pre_input_hook,
"get_pre_input_hook() -> function\n\
Get the current pre_input_hook function.");


static PyObject *
get_history_base(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(history_base);
}

PyDoc_STRVAR(doc_get_history_base,
"get_history_base() -> int\n\
Return the history base position.");


/* Internals */

static PyObject *
get_rl_point(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(rl_point);
}

PyDoc_STRVAR(doc_get_rl_point,
"get_rl_point() -> int\n\
Return rl_point.");


static PyObject *
get_rl_end(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(rl_end);
}

PyDoc_STRVAR(doc_get_rl_end,
"get_rl_end() -> int\n\
Return rl_end.");


extern char _rl_find_completion_word(int *fp, int *dp);

static PyObject *
find_completion_word(PyObject *self, PyObject *noargs)
{
	int begidx, endidx;
	PyObject *py_begidx, *py_endidx;

	/* The magic incantation */
	endidx = rl_point;
	if (rl_point)
		_rl_find_completion_word(NULL, NULL);
	begidx = rl_point;
	rl_point = endidx;

	py_begidx = PyInt_FromLong(begidx);
	py_endidx = PyInt_FromLong(endidx);

	if (!py_begidx || !py_endidx)
		return NULL;

	return PyTuple_Pack(2, py_begidx, py_endidx);
}

PyDoc_STRVAR(doc_find_completion_word,
"find_completion_word() -> (begidx, endidx)\n\
Find the bounds of the word at or before the cursor position.");


static PyObject *
complete_internal(PyObject *self, PyObject *args)
{
	char *what_to_do = NULL;
	int result = 1;

	if (!PyArg_ParseTuple(args, "s:complete_internal", &what_to_do)) {
		return NULL;
	}
	if (what_to_do) {
		result = rl_complete_internal(*what_to_do);
	}
	return PyInt_FromLong(result);
}

PyDoc_STRVAR(doc_complete_internal,
"complete_internal(what_to_do) -> int\n\
Complete the word at or before the cursor position.");


/* Word-break hook */

static PyObject *completion_word_break_hook = NULL;

static char *
on_completion_word_break_hook(void);


static PyObject *
set_completion_word_break_hook(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("completion_word_break_hook",
			&completion_word_break_hook, args);

	rl_completion_word_break_hook =
		completion_word_break_hook ?
		(rl_cpvfunc_t *)on_completion_word_break_hook : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_completion_word_break_hook,
"set_completion_word_break_hook([function]) -> None\n\
A function to call when readline is deciding where to separate words for word completion. \
The function is called as ``function(begidx, endidx)`` once for every completion, \
and should return a string of word break characters for the current completion, or None \
to indicate no change.");


static PyObject *
get_completion_word_break_hook(PyObject *self, PyObject *noargs)
{
	if (completion_word_break_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(completion_word_break_hook);
	return completion_word_break_hook;
}

PyDoc_STRVAR(doc_get_completion_word_break_hook,
"get_completion_word_break_hook() -> function\n\
A function to call when readline is deciding where to separate words for word completion.");


static char *
on_completion_word_break_hook(void)
{
	char *result = NULL;
	char *s = NULL;
	PyObject *r;
	int begidx, endidx;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	endidx = rl_point;
	if (rl_point) {
		/* Unhook ourselves to avoid infinite recursion */
		rl_completion_word_break_hook = NULL;
		_rl_find_completion_word(NULL, NULL);
		rl_completion_word_break_hook =
			(rl_cpvfunc_t *)on_completion_word_break_hook;
	}
	begidx = rl_point;
	rl_point = endidx;

	r = PyObject_CallFunction(completion_word_break_hook, "ii",
	                          begidx, endidx);
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = NULL;
	}
	else {
		s = PyString_AsString(r);
		if (s == NULL)
			goto error;
		result = strdup(s);
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Directory completion hook */

static PyObject *directory_completion_hook = NULL;

static int
on_directory_completion_hook(char **directory);


static PyObject *
set_directory_completion_hook(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("directory_completion_hook",
			&directory_completion_hook, args);

	rl_directory_completion_hook =
		directory_completion_hook ?
		(rl_icppfunc_t *)on_directory_completion_hook : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_directory_completion_hook,
"set_directory_completion_hook([function]) -> None\n\
This function is allowed to modify the directory portion of filenames readline completes. \
The function is called as ``function(dirname)`` and should return a new directory name or \
None to indicate no change. At the least, the function must perform all necessary \
dequoting.");


static PyObject *
get_directory_completion_hook(PyObject *self, PyObject *noargs)
{
	if (directory_completion_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(directory_completion_hook);
	return directory_completion_hook;
}

PyDoc_STRVAR(doc_get_directory_completion_hook,
"get_directory_completion_hook() -> function\n\
This function is allowed to modify the directory portion of filenames readline completes.");


static int
on_directory_completion_hook(char **directory)
{
	int result = 0;
	char *s = NULL;
	PyObject *r;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	r = PyObject_CallFunction(directory_completion_hook, "s", *directory);
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
		s = PyString_AsString(r);
		if (s == NULL)
			goto error;

		s = strdup(s);
		if (s != NULL) {
			free(*directory);
			*directory = s;
			result = 1;
		}
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Replace line buffer contents */

static PyObject *
replace_line(PyObject *self, PyObject *args)
{
	char *value = NULL;

	if (!PyArg_ParseTuple(args, "s:replace_line", &value)) {
		return NULL;
	}
	if (value) {
		rl_replace_line(value, 0);
		/* Move rl_point to end of line */
		rl_point = rl_end;
	}
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_replace_line,
"replace_line(string) -> None\n\
Replace the line buffer contents with string.");


/* Read a key (from the keyboard) */

static PyObject*
read_key(PyObject* self, PyObject* noargs)
{
	int c;

	RL_SETSTATE(RL_STATE_MOREINPUT);
	c = rl_read_key();
	RL_UNSETSTATE(RL_STATE_MOREINPUT);

	/* Clear KeyboardInterrupt since it's too late
	   now anyway */
	if (PyErr_CheckSignals() == -1 &&
	    PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
		PyErr_Clear();

	return PyString_FromFormat("%c", c);
}

PyDoc_STRVAR(doc_read_key,
"read_key() -> string\n\
Read a key from readline's input stream, typically the keyboard.");


/* Stuff a character into the input stream */

static PyObject *
stuff_char(PyObject *self, PyObject *args)
{
	char *value = NULL;
	int r = 0;

	if (!PyArg_ParseTuple(args, "s:stuff_char", &value)) {
		return NULL;
	}
	if (value && *value) {
		r = rl_stuff_char(*value);
	}
	return PyBool_FromLong(r);
}

PyDoc_STRVAR(doc_stuff_char,
"stuff_char(string) -> bool\n\
Insert a character into readline's input stream. \
Returns True if the insert was successful.");


/* Tilde expansion flag */

extern int rl_complete_with_tilde_expansion;

static PyObject *
get_complete_with_tilde_expansion(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(rl_complete_with_tilde_expansion);
}

PyDoc_STRVAR(doc_get_complete_with_tilde_expansion,
"get_complete_with_tilde_expansion() -> bool\n\
If True, readline completion functions perform tilde expansion.");


static PyObject *
set_complete_with_tilde_expansion(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_complete_with_tilde_expansion", &value)) {
		return NULL;
	}
	rl_complete_with_tilde_expansion = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_complete_with_tilde_expansion,
"set_complete_with_tilde_expansion(bool) -> None\n\
If True, readline completion functions perform tilde expansion.");


/* Match hidden files flag */

extern int _rl_match_hidden_files;

static PyObject *
get_match_hidden_files(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(_rl_match_hidden_files);
}

PyDoc_STRVAR(doc_get_match_hidden_files,
"get_match_hidden_files() -> bool\n\
If True, include hidden files when computing the list of matches.");


static PyObject *
set_match_hidden_files(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_match_hidden_files", &value)) {
		return NULL;
	}
	_rl_match_hidden_files = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_match_hidden_files,
"set_match_hidden_files(bool) -> None\n\
If True, include hidden files when computing the list of matches.");


/* StringArray helpers */

static char**
StringArray_new(size_t size)
{
	char **p;

	p = calloc(size+1, sizeof(char*));
	if (p == NULL)
		PyErr_NoMemory();
	return p;
}


static void
StringArray_free(char **strings)
{
	char **p;

	if (strings) {
		for (p = strings; *p; p++)
			free(*p);
		free(strings);
	}
}


static size_t
StringArray_size(char **strings)
{
	char **p;
	size_t size = 0;

	for (p = strings; *p; p++)
		size++;
	return size;
}


static int
StringArray_insert(char ***strings, size_t pos, char *string)
{
	char **new;
	char **p;
	size_t size, i;

	size = StringArray_size(*strings);
	if (size == -1)
		return -1;

	new = StringArray_new(size+1);
	if (new == NULL)
		return -1;

	for (p = *strings, i = 0; *p; p++) {
		if (i == pos)
			new[i++] = string;
		new[i++] = *p;
	}
	free(*strings);
	*strings = new;
	return 0;
}


/* StringArray to PyList and back */

static PyObject*
PyList_FromStringArray(char **strings)
{
	PyObject *list;
	PyObject *s;
	size_t size, i;

	size = StringArray_size(strings);
	if (size == -1)
		return NULL;

	list = PyList_New(size);
	if (list == NULL)
		return NULL;

	for (i = 0; i < size; i++) {
		s = PyString_FromString(strings[i]);
		if (s == NULL)
			goto error;
		if (PyList_SetItem(list, i, s) == -1)
			goto error;
	}
	return list;
  error:
	Py_XDECREF(list);
	return NULL;
}


static char**
PyList_AsStringArray(PyObject *list)
{
	char **strings;
	char **p;
	char *s;
	PyObject *r;
	Py_ssize_t size, i;

	size = PyList_Size(list);
	if (size == -1)
		return NULL;

	strings = StringArray_new(size);
	if (strings == NULL)
		return NULL;

	for (p = strings, i = 0; i < size; i++) {
		r = PyList_GetItem(list, i);
		if (r == NULL)
			goto error;
		s = PyString_AsString(r);
		if (s == NULL)
			goto error;
		s = strdup(s);
		if (s == NULL) {
			PyErr_NoMemory();
			goto error;
		}
		*p++ = s;
	}
	return strings;
  error:
	StringArray_free(strings);
	return NULL;
}


/* Display match list function */

static PyObject*
display_match_list(PyObject *self, PyObject *args)
{
	char *substitution = NULL;
	PyObject *matches = NULL;
	Py_ssize_t num_matches = 0;
	int max_length = 0;
	char **strings;
	char *s;

	if (!PyArg_ParseTuple(args, "sOi:display_match_list",
			      &substitution, &matches, &max_length)) {
		return NULL;
	}

	num_matches = PyList_Size(matches);
	if (num_matches == -1)
		return NULL;

	strings = PyList_AsStringArray(matches);
	if (strings == NULL)
		return NULL;

	s = strdup(substitution);
	if (s == NULL) {
		PyErr_NoMemory();
		goto error;
	}

	/* Put the substitution back into the list at position 0 */
	if (StringArray_insert(&strings, 0, s) == -1)
		goto error;

	rl_display_match_list(strings, num_matches, max_length);
	rl_forced_update_display();
	rl_display_fixed = 1;

	/* Clear KeyboardInterrupt */
	if (PyErr_CheckSignals() == -1 &&
	    PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
		PyErr_Clear();

	StringArray_free(strings);
	Py_RETURN_NONE;
  error:
	StringArray_free(strings);
	return NULL;
}

PyDoc_STRVAR(doc_display_match_list,
"display_match_list(substitution, matches, longest_match_length) -> None\n\
Display a list of matches in columnar format on readline's output stream.");


/* Ignore some completions function */

static PyObject *ignore_some_completions_function = NULL;

static int
on_ignore_some_completions_function(char **directory);


static PyObject *
set_ignore_some_completions_function(PyObject *self, PyObject *args)
{
	PyObject *result = set_hook("ignore_some_completions_function",
			&ignore_some_completions_function, args);

	rl_ignore_some_completions_function =
		ignore_some_completions_function ?
		(rl_compignore_func_t *)on_ignore_some_completions_function : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_ignore_some_completions_function,
"set_ignore_some_completions_function([function]) -> None\n\
This function may filter the results of filename completion. \
The function is called as ``function(substitution, matches)`` and \
should return a filtered subset of matches or None to indicate no \
change.");


static PyObject *
get_ignore_some_completions_function(PyObject *self, PyObject *noargs)
{
	if (ignore_some_completions_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(ignore_some_completions_function);
	return ignore_some_completions_function;
}

PyDoc_STRVAR(doc_get_ignore_some_completions_function,
"get_ignore_some_completions_function() -> function\n\
This function may filter the results of filename completion.");


static int
on_ignore_some_completions_function(char **matches)
{
	int result = 0;
	char **strings;
	size_t i;
	Py_ssize_t old_size, new_size;
	PyObject *m = NULL;
	PyObject *r = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	m = PyList_FromStringArray(matches+1);
	if (m == NULL)
		goto error;

	r = PyObject_CallFunction(ignore_some_completions_function, "sO",
				  matches[0], m);
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
		new_size = PyList_Size(r);
		if (new_size == -1)
			goto error;

		old_size = PyList_Size(m);
		if (new_size > old_size)
			goto error;

		strings = PyList_AsStringArray(r);
		if (strings == NULL)
			goto error;

		for (i=1; i <= old_size; i++)
			free(matches[i]);

		for (i=1; i <= new_size; i++) {
			matches[i] = strings[i-1];
			matches[i+1] = NULL;
		}
		free(strings);
		result = 1;
	}
	Py_DECREF(m);
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(m);
	Py_XDECREF(r);
  done:
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* </_readline.c> */


/* Table of functions exported by the module */

static struct PyMethodDef readline_methods[] =
{
	{"parse_and_bind", parse_and_bind, METH_VARARGS, doc_parse_and_bind},
	{"get_line_buffer", get_line_buffer, METH_NOARGS, doc_get_line_buffer},
	{"insert_text", insert_text, METH_VARARGS, doc_insert_text},
	{"redisplay", redisplay, METH_VARARGS, doc_redisplay},
	{"read_init_file", read_init_file, METH_VARARGS, doc_read_init_file},
	{"read_history_file", read_history_file,
	 METH_VARARGS, doc_read_history_file},
	{"write_history_file", write_history_file,
	 METH_VARARGS, doc_write_history_file},
	{"get_history_item", get_history_item,
	 METH_VARARGS, doc_get_history_item},
	{"get_current_history_length", (PyCFunction)get_current_history_length,
	 METH_NOARGS, doc_get_current_history_length},
	{"set_history_length", set_history_length,
	 METH_VARARGS, set_history_length_doc},
	{"get_history_length", get_history_length,
	 METH_NOARGS, get_history_length_doc},
	{"set_completer", set_completer, METH_VARARGS, doc_set_completer},
	{"get_completer", get_completer, METH_NOARGS, doc_get_completer},
	{"get_completion_type", get_completion_type,
	 METH_NOARGS, doc_get_completion_type},
	{"get_begidx", get_begidx, METH_NOARGS, doc_get_begidx},
	{"get_endidx", get_endidx, METH_NOARGS, doc_get_endidx},

	{"set_completer_delims", set_completer_delims,
	 METH_VARARGS, doc_set_completer_delims},
	{"add_history", py_add_history, METH_VARARGS, doc_add_history},
	{"remove_history_item", py_remove_history, METH_VARARGS, doc_remove_history},
	{"replace_history_item", py_replace_history, METH_VARARGS, doc_replace_history},
	{"get_completer_delims", get_completer_delims,
	 METH_NOARGS, doc_get_completer_delims},

	{"set_completion_display_matches_hook", set_completion_display_matches_hook,
	 METH_VARARGS, doc_set_completion_display_matches_hook},
	{"set_startup_hook", set_startup_hook,
	 METH_VARARGS, doc_set_startup_hook},
#ifdef HAVE_RL_PRE_INPUT_HOOK
	{"set_pre_input_hook", set_pre_input_hook,
	 METH_VARARGS, doc_set_pre_input_hook},
#endif
#ifdef HAVE_RL_COMPLETION_APPEND_CHARACTER
	{"clear_history", py_clear_history, METH_NOARGS, doc_clear_history},

	/* <_readline.c> */
	{"get_completion_append_character", get_completion_append_character,
	 METH_NOARGS, doc_get_completion_append_character},
	{"set_completion_append_character", set_completion_append_character,
	 METH_VARARGS, doc_set_completion_append_character},
#endif
	{"get_completion_suppress_append", get_completion_suppress_append,
	 METH_NOARGS, doc_get_completion_suppress_append},
	{"set_completion_suppress_append", set_completion_suppress_append,
	 METH_VARARGS, doc_set_completion_suppress_append},
	{"get_completer_quote_characters", get_completer_quote_characters,
	 METH_NOARGS, doc_get_completer_quote_characters},
	{"set_completer_quote_characters", set_completer_quote_characters,
	 METH_VARARGS, doc_set_completer_quote_characters},
	{"get_filename_quote_characters", get_filename_quote_characters,
	 METH_NOARGS, doc_get_filename_quote_characters},
	{"set_filename_quote_characters", set_filename_quote_characters,
	 METH_VARARGS, doc_set_filename_quote_characters},
	{"get_completion_found_quote", get_completion_found_quote,
	 METH_NOARGS, doc_get_completion_found_quote},
	{"get_completion_quote_character", get_completion_quote_character,
	 METH_NOARGS, doc_get_completion_quote_character},
	{"get_completion_suppress_quote", get_completion_suppress_quote,
	 METH_NOARGS, doc_get_completion_suppress_quote},
	{"set_completion_suppress_quote", set_completion_suppress_quote,
	 METH_VARARGS, doc_set_completion_suppress_quote},
	{"get_filename_completion_desired", get_filename_completion_desired,
	 METH_NOARGS, doc_get_filename_completion_desired},
	{"set_filename_completion_desired", set_filename_completion_desired,
	 METH_VARARGS, doc_set_filename_completion_desired},
	{"get_filename_quoting_desired", get_filename_quoting_desired,
	 METH_NOARGS, doc_get_filename_quoting_desired},
	{"set_filename_quoting_desired", set_filename_quoting_desired,
	 METH_VARARGS, doc_set_filename_quoting_desired},
	/*
	{"get_attempted_completion_over", get_attempted_completion_over,
	 METH_NOARGS, doc_get_attempted_completion_over},
	{"set_attempted_completion_over", set_attempted_completion_over,
	 METH_VARARGS, doc_set_attempted_completion_over},
	*/
	{"filename_completion_function", filename_completion_function,
	 METH_VARARGS, doc_filename_completion_function},
	{"username_completion_function", username_completion_function,
	 METH_VARARGS, doc_username_completion_function},
	{"get_special_prefixes", get_special_prefixes,
	 METH_NOARGS, doc_get_special_prefixes},
	{"set_special_prefixes", set_special_prefixes,
	 METH_VARARGS, doc_set_special_prefixes},
	{"get_completion_query_items", get_completion_query_items,
	 METH_NOARGS, doc_get_completion_query_items},
	{"set_completion_query_items", set_completion_query_items,
	 METH_VARARGS, doc_set_completion_query_items},
	{"get_filename_quoting_function", get_filename_quoting_function,
	 METH_NOARGS, doc_get_filename_quoting_function},
	{"set_filename_quoting_function", set_filename_quoting_function,
	 METH_VARARGS, doc_set_filename_quoting_function},
	{"get_filename_dequoting_function", get_filename_dequoting_function,
	 METH_NOARGS, doc_get_filename_dequoting_function},
	{"set_filename_dequoting_function", set_filename_dequoting_function,
	 METH_VARARGS, doc_set_filename_dequoting_function},
	{"get_char_is_quoted_function", get_char_is_quoted_function,
	 METH_NOARGS, doc_get_char_is_quoted_function},
	{"set_char_is_quoted_function", set_char_is_quoted_function,
	 METH_VARARGS, doc_set_char_is_quoted_function},
	{"get_completion_display_matches_hook", get_completion_display_matches_hook,
	 METH_NOARGS, doc_get_completion_display_matches_hook},
	{"get_startup_hook", get_startup_hook,
	 METH_NOARGS, doc_get_startup_hook},
#ifdef HAVE_RL_PRE_INPUT_HOOK
	{"get_pre_input_hook", get_pre_input_hook,
	 METH_NOARGS, doc_get_pre_input_hook},
#endif
	/* readline 6
	{"get_completion_invoking_key", get_completion_invoking_key,
	 METH_NOARGS, doc_get_completion_invoking_key},
	{"get_sort_completion_matches", get_sort_completion_matches,
	 METH_NOARGS, doc_get_sort_completion_matches},
	{"set_sort_completion_matches", set_sort_completion_matches,
	 METH_VARARGS, doc_set_sort_completion_matches},
	{"get_ignore_completion_duplicates", get_ignore_completion_duplicates,
	 METH_NOARGS, doc_get_ignore_completion_duplicates},
	{"set_ignore_completion_duplicates", set_ignore_completion_duplicates,
	 METH_VARARGS, doc_set_ignore_completion_duplicates},
	{"get_completion_mark_symlink_dirs", get_completion_mark_symlink_dirs,
	 METH_NOARGS, doc_get_completion_mark_symlink_dirs},
	{"set_completion_mark_symlink_dirs", set_completion_mark_symlink_dirs,
	 METH_VARARGS, doc_set_completion_mark_symlink_dirs},
	*/
	{"get_inhibit_completion", get_inhibit_completion,
	 METH_NOARGS, doc_get_inhibit_completion},
	{"set_inhibit_completion", set_inhibit_completion,
	 METH_VARARGS, doc_set_inhibit_completion},
	{"get_completion_word_break_hook", get_completion_word_break_hook,
	 METH_NOARGS, doc_get_completion_word_break_hook},
	{"set_completion_word_break_hook", set_completion_word_break_hook,
	 METH_VARARGS, doc_set_completion_word_break_hook},
	{"get_directory_completion_hook", get_directory_completion_hook,
	 METH_NOARGS, doc_get_directory_completion_hook},
	{"set_directory_completion_hook", set_directory_completion_hook,
	 METH_VARARGS, doc_set_directory_completion_hook},
	{"get_complete_with_tilde_expansion", get_complete_with_tilde_expansion,
	 METH_NOARGS, doc_get_complete_with_tilde_expansion},
	{"set_complete_with_tilde_expansion", set_complete_with_tilde_expansion,
	 METH_VARARGS, doc_set_complete_with_tilde_expansion},
	{"get_match_hidden_files", get_match_hidden_files,
	 METH_NOARGS, doc_get_match_hidden_files},
	{"set_match_hidden_files", set_match_hidden_files,
	 METH_VARARGS, doc_set_match_hidden_files},
	{"get_ignore_some_completions_function", get_ignore_some_completions_function,
	 METH_NOARGS, doc_get_ignore_some_completions_function},
	{"set_ignore_some_completions_function", set_ignore_some_completions_function,
	 METH_VARARGS, doc_set_ignore_some_completions_function},
	{"get_history_base", get_history_base,
	 METH_NOARGS, doc_get_history_base},
	{"tilde_expand", py_tilde_expand, METH_VARARGS, doc_tilde_expand},
	{"replace_line", replace_line, METH_VARARGS, doc_replace_line},
	{"read_key", read_key, METH_NOARGS, doc_read_key},
	{"stuff_char", stuff_char, METH_VARARGS, doc_stuff_char},
	{"display_match_list", display_match_list,
	 METH_VARARGS, doc_display_match_list},
	{"get_rl_point", get_rl_point, METH_NOARGS, doc_get_rl_point},
	{"get_rl_end", get_rl_end, METH_NOARGS, doc_get_rl_end},
	{"find_completion_word", find_completion_word,
	 METH_NOARGS, doc_find_completion_word},
	{"complete_internal", complete_internal,
	 METH_VARARGS, doc_complete_internal},
	/* </_readline.c> */

	{0, 0}
};


/* C function to call the Python hooks. */

static int
on_hook(PyObject *func)
{
	int result = 0;
	if (func != NULL) {
		PyObject *r;
#ifdef WITH_THREAD
		PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
		r = PyObject_CallFunction(func, NULL);
		if (r == NULL)
			goto error;
		if (r == Py_None)
			result = 0;
		else {
			result = PyInt_AsLong(r);
			if (result == -1 && PyErr_Occurred()) 
				goto error;
		}
		Py_DECREF(r);
		goto done;
	  error:
		PyErr_Clear();
		Py_XDECREF(r);
	  done:
#ifdef WITH_THREAD
		PyGILState_Release(gilstate);
#endif
		return result;
	}
	return result;
}

static int
on_startup_hook(void)
{
	return on_hook(startup_hook);
}

#ifdef HAVE_RL_PRE_INPUT_HOOK
static int
on_pre_input_hook(void)
{
	return on_hook(pre_input_hook);
}
#endif


/* C function to call the Python completion_display_matches */

static void
on_completion_display_matches_hook(char **matches,
				   int num_matches, int max_length)
{
	PyObject *m=NULL, *r=NULL;
#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	m = PyList_FromStringArray(matches+1);
	if (m == NULL)
		goto error;

	r = PyObject_CallFunction(completion_display_matches_hook,
				  "sOi", matches[0], m, max_length);

	Py_DECREF(m), m=NULL;
	
	if (r == NULL ||
	    (r != Py_None && PyInt_AsLong(r) == -1 && PyErr_Occurred())) {
		goto error;
	}
	Py_XDECREF(r), r=NULL;

	if (0) {
	error:
		PyErr_Clear();
		Py_XDECREF(m);
		Py_XDECREF(r);
	}
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
}


/* C function to call the Python completer. */

static char *
on_completion(const char *text, int state)
{
	char *result = NULL;
	if (completer != NULL) {
		PyObject *r;
#ifdef WITH_THREAD	      
		PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
		rl_attempted_completion_over = 1;
		r = PyObject_CallFunction(completer, "si", text, state);
		if (r == NULL)
			goto error;
		if (r == Py_None) {
			result = NULL;
		}
		else {
			char *s = PyString_AsString(r);
			if (s == NULL)
				goto error;
			result = strdup(s);
		}
		Py_DECREF(r);
		goto done;
	  error:
		PyErr_Clear();
		Py_XDECREF(r);
	  done:
#ifdef WITH_THREAD	      
		PyGILState_Release(gilstate);
#endif
		return result;
	}
	return result;
}


/* A more flexible constructor that saves the "begidx" and "endidx"
 * before calling the normal completer */

static char **
flex_complete(char *text, int start, int end)
{
	Py_XDECREF(begidx);
	Py_XDECREF(endidx);
	begidx = PyInt_FromLong((long) start);
	endidx = PyInt_FromLong((long) end);

	/* Reset completion variables like readline 6 does */
	rl_completion_append_character = ' ';
	rl_completion_suppress_append = 0;
	rl_completion_suppress_quote = 0;
	rl_filename_completion_desired = 0;
	rl_filename_quoting_desired = 1;

	return completion_matches(text, *on_completion);
}


/* Helper to initialize GNU readline properly. */

static void
setup_readline(void)
{
#ifdef SAVE_LOCALE
	char *saved_locale = strdup(setlocale(LC_CTYPE, NULL));
	if (!saved_locale)
		Py_FatalError("not enough memory to save locale");
#endif

	using_history();

	rl_readline_name = "python";
#if defined(PYOS_OS2) && defined(PYCC_GCC)
	/* Allow $if term= in .inputrc to work */
	rl_terminal_name = getenv("TERM");
#endif
	/* Force rebind of TAB to insert-tab */
	rl_bind_key('\t', rl_insert);
	/* Bind both ESC-TAB and ESC-ESC to the completion function */
	rl_bind_key_in_map ('\t', rl_complete, emacs_meta_keymap);
	rl_bind_key_in_map ('\033', rl_complete, emacs_meta_keymap);
	/* Set our hook functions */
	rl_startup_hook = (Function *)on_startup_hook;
#ifdef HAVE_RL_PRE_INPUT_HOOK
	rl_pre_input_hook = (Function *)on_pre_input_hook;
#endif
	/* Set our completion function */
	rl_attempted_completion_function = (CPPFunction *)flex_complete;
	/* Set Python word break characters */
	rl_completer_word_break_characters =
		strdup(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>/?");
		/* All nonalphanums except '.' */
#ifdef HAVE_RL_COMPLETION_APPEND_CHARACTER
	rl_completion_append_character = ' ';
#endif
	/* Save a reference to the default implementation */
	default_filename_quoting_function = rl_filename_quoting_function;

	begidx = PyInt_FromLong(0L);
	endidx = PyInt_FromLong(0L);
	/* Initialize (allows .inputrc to override)
	 *
	 * XXX: A bug in the readline-2.2 library causes a memory leak
	 * inside this function.  Nothing we can do about it.
	 */
	rl_initialize();

	RESTORE_LOCALE(saved_locale)
}

/* Wrapper around GNU readline that handles signals differently. */


#if defined(HAVE_RL_CALLBACK) && defined(HAVE_SELECT)

static	char *completed_input_string;
static void
rlhandler(char *text)
{
	completed_input_string = text;
	rl_callback_handler_remove();
}

extern PyThreadState* _PyOS_ReadlineTState;

static char *
readline_until_enter_or_signal(char *prompt, int *signal)
{
	char * not_done_reading = "";
	fd_set selectset;

	*signal = 0;
#ifdef HAVE_RL_CATCH_SIGNAL
	rl_catch_signals = 0;
#endif

	rl_callback_handler_install (prompt, rlhandler);
	FD_ZERO(&selectset);
	
	completed_input_string = not_done_reading;

	while (completed_input_string == not_done_reading) {
		int has_input = 0;

		while (!has_input)
		{	struct timeval timeout = {0, 100000}; /* 0.1 seconds */

			/* [Bug #1552726] Only limit the pause if an input hook has been 
			   defined.  */
			struct timeval *timeoutp = NULL;
			if (PyOS_InputHook) 
				timeoutp = &timeout;
			FD_SET(fileno(rl_instream), &selectset);
			/* select resets selectset if no input was available */
			has_input = select(fileno(rl_instream) + 1, &selectset,
					   NULL, NULL, timeoutp);
			if(PyOS_InputHook) PyOS_InputHook();
		}

		if(has_input > 0) {
			rl_callback_read_char();
		}
		else if (errno == EINTR) {
			int s;
#ifdef WITH_THREAD
			PyEval_RestoreThread(_PyOS_ReadlineTState);
#endif
			s = PyErr_CheckSignals();
#ifdef WITH_THREAD
			PyEval_SaveThread();	
#endif
			if (s < 0) {
				rl_free_line_state();
				rl_cleanup_after_signal();
				rl_callback_handler_remove();
				*signal = 1;
				completed_input_string = NULL;
			}
		}
	}

	return completed_input_string;
}


#else

/* Interrupt handler */

static jmp_buf jbuf;

/* ARGSUSED */
static void
onintr(int sig)
{
	longjmp(jbuf, 1);
}


static char *
readline_until_enter_or_signal(char *prompt, int *signal)
{
	PyOS_sighandler_t old_inthandler;
	char *p;
    
	*signal = 0;

	old_inthandler = PyOS_setsig(SIGINT, onintr);
	if (setjmp(jbuf)) {
#ifdef HAVE_SIGRELSE
		/* This seems necessary on SunOS 4.1 (Rasmus Hahn) */
		sigrelse(SIGINT);
#endif
		PyOS_setsig(SIGINT, old_inthandler);
		*signal = 1;
		return NULL;
	}
	rl_event_hook = PyOS_InputHook;
	p = readline(prompt);
	PyOS_setsig(SIGINT, old_inthandler);

    return p;
}
#endif /*defined(HAVE_RL_CALLBACK) && defined(HAVE_SELECT) */


static char *
call_readline(FILE *sys_stdin, FILE *sys_stdout, char *prompt)
{
	size_t n;
	char *p, *q;
	int signal;

#ifdef SAVE_LOCALE
	char *saved_locale = strdup(setlocale(LC_CTYPE, NULL));
	if (!saved_locale)
		Py_FatalError("not enough memory to save locale");
	setlocale(LC_CTYPE, "");
#endif

	if (sys_stdin != rl_instream || sys_stdout != rl_outstream) {
		rl_instream = sys_stdin;
		rl_outstream = sys_stdout;
#ifdef HAVE_RL_COMPLETION_APPEND_CHARACTER
		rl_prep_terminal (1);
#endif
	}

	p = readline_until_enter_or_signal(prompt, &signal);
	
	/* we got an interrupt signal */
	if (signal) {
		RESTORE_LOCALE(saved_locale)
		return NULL;
	}

	/* We got an EOF, return a empty string. */
	if (p == NULL) {
		p = PyMem_Malloc(1);
		if (p != NULL)
			*p = '\0';
		RESTORE_LOCALE(saved_locale)
		return p;
	}

	/* we have a valid line */
	n = strlen(p);
	if (n > 0) {
		char *line;
		HISTORY_STATE *state = history_get_history_state();
		if (state->length > 0)
			line = history_get(state->length)->line;
		else
			line = "";
		if (strcmp(p, line))
			add_history(p);
		/* the history docs don't say so, but the address of state
		   changes each time history_get_history_state is called
		   which makes me think it's freshly malloc'd memory...
		   on the other hand, the address of the last line stays the
		   same as long as history isn't extended, so it appears to
		   be malloc'd but managed by the history package... */
		free(state);
	}
	/* Copy the malloc'ed buffer into a PyMem_Malloc'ed one and
	   release the original. */
	q = p;
	p = PyMem_Malloc(n+2);
	if (p != NULL) {
		strncpy(p, q, n);
		p[n] = '\n';
		p[n+1] = '\0';
	}
	free(q);
	RESTORE_LOCALE(saved_locale)
	return p;
}


/* Initialize the module */

PyDoc_STRVAR(doc_module,
"Importing this module enables command line editing using GNU readline.");

PyMODINIT_FUNC
init_readline(void)
{
	PyObject *m;

	m = Py_InitModule4("_readline", readline_methods, doc_module,
			   (PyObject *)NULL, PYTHON_API_VERSION);
	if (m == NULL)
		return;

	PyOS_ReadlineFunctionPointer = call_readline;
	setup_readline();
}

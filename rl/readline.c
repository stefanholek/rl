/* Alternative Python bindings for GNU Readline
 *
 * Based on the readline.c source of Pyton 2.7.
 * Author: Stefan H. Holek
 */

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

/* GNU Readline definitions */
#undef HAVE_CONFIG_H  /* Else readline/chardefs.h includes strings.h */
#define _FUNCTION_DEF /* Else readline/rltypedefs.h defines old-style types */
#ifdef __STDC__
#define PREFER_STDARG /* Use ANSI C function prototypes */
#define USE_VARARGS
#endif
#include <readline/readline.h>
#include <readline/history.h>

#define completion_matches(x, y) \
	rl_completion_matches((x), ((rl_compentry_func_t *)(y)))

/* Custom definitions */
#include "stringarray.h"
#include "unicode.h"
#include "iterator.h"
#include "modulestate.h"

/* Python 3 compatibility */
#if (PY_MAJOR_VERSION >= 3)
#define PyInt_FromLong PyLong_FromLong
#define PyInt_AsLong _PyLong_AsInt
#define PyString_FromString PyUnicode_DECODE
#endif

/* _PyLong_AsInt appeared in Python 3.3.2 */
#if (PY_VERSION_HEX < 0x03030200)
#define _PyLong_AsInt PyLong_AsLong
#endif

/* PyMem_RawMalloc appeared in Python 3.4 */
#if (PY_VERSION_HEX < 0x03040000)
#define PyMem_RawMalloc PyMem_Malloc
#endif

/* _Py_SetLocaleFromEnv appeared in Python 3.7 */
#if (PY_VERSION_HEX < 0x03070000)
#if __ANDROID__
#define _Py_SetLocaleFromEnv(c) setlocale((c), "C.UTF-8")
#else
#define _Py_SetLocaleFromEnv(c) setlocale((c), "")
#endif
#endif


/* Exported function to send one line to readline's init file parser */

static PyObject *
parse_and_bind(PyObject *self, PyObject *args)
{
	char *s=NULL, *copy;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:parse_and_bind", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:parse_and_bind", &s))
		return NULL;
#endif
	/* Make a copy -- rl_parse_and_bind() modifies its argument */
	/* Bernard Herzog */
	copy = strdup(s);
	Py_XDECREF(b);
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
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "|O&:read_init_file", PyUnicode_FSOrNoneConverter, &b))
		return NULL;
	if (b != NULL)
		s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "|z:read_init_file", &s))
		return NULL;
#endif
	/* Treat empty string like an error here */
	if (s != NULL && *s == '\0')
		errno = 2;
	else
		/* rl_read_init_file calls tilde_expand internally */
		errno = rl_read_init_file(s);
	Py_XDECREF(b);
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
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "|O&:read_history_file", PyUnicode_FSOrNoneConverter, &b))
		return NULL;
	if (b != NULL)
		s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "|z:read_history_file", &s))
		return NULL;
#endif
	if (s != NULL && *s == '~') {
		s = tilde_expand(s);
		errno = read_history(s);
		free(s);
	}
	else
		errno = read_history(s);
	Py_XDECREF(b);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_read_history_file,
"read_history_file([filename]) -> None\n\
Load a readline history file.\n\
The default filename is ~/.history.");


/* Exported function to save a readline history file */

static int history_file_length = -1; /* do not truncate history by default */


static int
_py_write_history(const char *s)
{
	int saved_errno = errno = write_history(s);
	if (!saved_errno && history_file_length >= 0)
		history_truncate_file(s, history_file_length);
	return saved_errno;
}


static PyObject *
write_history_file(PyObject *self, PyObject *args)
{
	char *s = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "|O&:write_history_file", PyUnicode_FSOrNoneConverter, &b))
		return NULL;
	if (b != NULL)
		s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "|z:write_history_file", &s))
		return NULL;
#endif
	if (s != NULL && *s == '~') {
		s = tilde_expand(s);
		errno = _py_write_history(s);
		free(s);
	}
	else
		errno = _py_write_history(s);
	Py_XDECREF(b);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_write_history_file,
"write_history_file([filename]) -> None\n\
Save a readline history file.\n\
The default filename is ~/.history.");


/* Exported function to append to a readline history file */

static int
_py_append_history(int n, const char *s)
{
	int saved_errno = errno = append_history(n, s);
	if (!saved_errno && history_file_length >= 0)
		history_truncate_file(s, history_file_length);
	return saved_errno;
}


static PyObject *
append_history_file(PyObject *self, PyObject *args)
{
	int n;
	char *s = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "i|O&:append_history_file", &n, PyUnicode_FSOrNoneConverter, &b))
		return NULL;
	if (b != NULL)
		s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "i|z:append_history_file", &n, &s))
		return NULL;
#endif
	if (s != NULL && *s == '~') {
		s = tilde_expand(s);
		errno = _py_append_history(n, s);
		free(s);
	}
	else
		errno = _py_append_history(n, s);
	Py_XDECREF(b);
	if (errno)
		return PyErr_SetFromErrno(PyExc_IOError);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_append_history_file,
"append_history_file(nelements[, filename]) -> None\n\
Append the last ``nelements`` of the history to a readline history file.\n\
The default filename is ~/.history.");


/* Set history file length */

static PyObject*
set_history_length(PyObject *self, PyObject *args)
{
	int length = history_file_length;
	if (!PyArg_ParseTuple(args, "i:set_history_length", &length))
		return NULL;
	history_file_length = length;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(set_history_length_doc,
"set_history_length(int) -> None\n\
Set the maximum number of items written to\n\
the history file. A negative value inhibits\n\
history file truncation.");


/* Get history file length */

static PyObject*
get_history_length(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(history_file_length);
}

PyDoc_STRVAR(get_history_length_doc,
"get_history_length() -> int\n\
Return the maximum number of items written to\n\
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
		Py_CLEAR(*hook_var);
	}
	else if (PyCallable_Check(function)) {
		PyObject *tmp = *hook_var;
		Py_INCREF(function);
		*hook_var = function;
		Py_XDECREF(tmp);
	}
	else {
		PyErr_Format(PyExc_TypeError,
			     "set_%.50s(func): argument not callable",
			     funcname);
		return NULL;
	}
	Py_RETURN_NONE;
}


/* Exported functions to specify hook functions in Python */

/* Startup hook */

static int
on_startup_hook(void);


static PyObject *
set_startup_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("startup_hook", &global->startup_hook, args);

	rl_startup_hook =
		global->startup_hook ?
		(rl_hook_func_t *)on_startup_hook : NULL;
	return result;
}

PyDoc_STRVAR(doc_set_startup_hook,
"set_startup_hook([function]) -> None\n\
Set or remove the startup_hook function.\n\
The function is called with no arguments just\n\
before readline prints the first prompt.");


static PyObject *
get_startup_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->startup_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->startup_hook);
	return global->startup_hook;
}

PyDoc_STRVAR(doc_get_startup_hook,
"get_startup_hook() -> function\n\
Get the current startup_hook function.");


/* Pre-input hook */

static int
on_pre_input_hook(void);


static PyObject *
set_pre_input_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("pre_input_hook", &global->pre_input_hook, args);

	rl_pre_input_hook =
		global->pre_input_hook ?
		(rl_hook_func_t *)on_pre_input_hook : NULL;
	return result;
}

PyDoc_STRVAR(doc_set_pre_input_hook,
"set_pre_input_hook([function]) -> None\n\
Set or remove the pre_input_hook function.\n\
The function is called with no arguments after the first prompt\n\
has been printed and just before readline starts reading input\n\
characters.");


static PyObject *
get_pre_input_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->pre_input_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->pre_input_hook);
	return global->pre_input_hook;
}

PyDoc_STRVAR(doc_get_pre_input_hook,
"get_pre_input_hook() -> function\n\
Get the current pre_input_hook function.");


/* Display matches hook */

static void
on_completion_display_matches_hook(char **matches, int num_matches, int max_length);

static void
default_display_matches_hook(char **matches, int num_matches, int max_length);


static PyObject *
set_completion_display_matches_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("completion_display_matches_hook",
			&global->completion_display_matches_hook, args);

	rl_completion_display_matches_hook =
		global->completion_display_matches_hook ?
		(rl_compdisp_func_t *)on_completion_display_matches_hook :
		(rl_compdisp_func_t *)default_display_matches_hook;
	return result;

}

PyDoc_STRVAR(doc_set_completion_display_matches_hook,
"set_completion_display_matches_hook([function]) -> None\n\
Set or remove the completion display function.\n\
The function is called as \
  ``function(substitution, matches, longest_match_length)`` \
once each time matches need to be displayed.");


static PyObject *
get_completion_display_matches_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->completion_display_matches_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->completion_display_matches_hook);
	return global->completion_display_matches_hook;
}

PyDoc_STRVAR(doc_get_completion_display_matches_hook,
"get_completion_display_matches_hook() -> function\n\
Get the current completion display function.");


/* Exported functions to specify a word completer in Python */

static Py_ssize_t begidx = 0;
static Py_ssize_t endidx = 0;

static void _py_set_completion_defaults(void);


static PyObject *
set_completer(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	return set_hook("completer", &global->completer, args);
}

PyDoc_STRVAR(doc_set_completer,
"set_completer([function]) -> None\n\
Set or remove the completion entry function.\n\
The function is called as ``function(text, state)``,\n\
for ``state`` in 0, 1, 2, ..., until it returns None.\n\
It should return the next possible completion starting with ``text``.");


static PyObject *
get_completer(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->completer == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->completer);
	return global->completer;
}

PyDoc_STRVAR(doc_get_completer,
"get_completer() -> function\n\
\n\
Get the current completion entry function.");


/* Get/set the completion type for the scope of the tab-completion */

static PyObject *
get_completion_type(PyObject *self, PyObject *noarg)
{
#if (PY_MAJOR_VERSION >= 3)
	return PyUnicode_DECODE_CHAR(rl_completion_type);
#else
	if (!rl_completion_type)
		return PyString_FromString("");
	return PyString_FromFormat("%c", rl_completion_type);
#endif
}

PyDoc_STRVAR(doc_get_completion_type,
"get_completion_type() -> string\n\
Get the type of completion being attempted.");


static PyObject *
set_completion_type(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_completion_type", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_completion_type", &s))
		return NULL;
#endif
	rl_completion_type = (s && *s) ? *s : '\0';
	Py_XDECREF(b);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_type,
"set_completion_type(string) -> None\n\
Set the type of completion being attempted.");


/* Get/set the beginning index for the scope of the tab-completion */

static PyObject *
get_begidx(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(begidx);
}

PyDoc_STRVAR(doc_get_begidx,
"get_begidx() -> int\n\
Get the beginning index of the readline tab-completion scope.");


static PyObject *
set_begidx(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_begidx", &value)) {
		return NULL;
	}
	begidx = value;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_begidx,
"set_begidx(int) -> None\n\
Set the beginning index of the readline tab-completion scope.");


/* Get/set the ending index for the scope of the tab-completion */

static PyObject *
get_endidx(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(endidx);
}

PyDoc_STRVAR(doc_get_endidx,
"get_endidx() -> int\n\
Get the ending index of the readline tab-completion scope.");


static PyObject *
set_endidx(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_endidx", &value)) {
		return NULL;
	}
	endidx = value;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_endidx,
"set_endidx(int) -> None\n\
Set the ending index of the readline tab-completion scope.");


/* Get/set the tab-completion word-delimiters that readline uses */

static PyObject *
get_completer_delims(PyObject *self, PyObject *noarg)
{
	if (!rl_completer_word_break_characters)
		return PyString_FromString("");
	return PyString_FromString(rl_completer_word_break_characters);
}

PyDoc_STRVAR(doc_get_completer_delims,
"get_completer_delims() -> string\n\
Get the readline word delimiters for tab-completion.");


static PyObject *
set_completer_delims(PyObject *self, PyObject *args)
{
	char *break_chars;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_completer_delims", PyUnicode_StrConverter, &b))
		return NULL;
	break_chars = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_completer_delims", &break_chars))
		return NULL;
#endif
	break_chars = strdup(break_chars);
	Py_XDECREF(b);

	if (break_chars) {
		if (rl_completer_word_break_characters &&
		    rl_completer_word_break_characters != rl_basic_word_break_characters)
			free((void*)rl_completer_word_break_characters);
		rl_completer_word_break_characters = break_chars;
		Py_RETURN_NONE;
	}
	else
		return PyErr_NoMemory();
}

PyDoc_STRVAR(doc_set_completer_delims,
"set_completer_delims(string) -> None\n\
Set the readline word delimiters for tab-completion.");


/* Free memory allocated for a history entry
   https://bugs.python.org/issue9450
   https://bugs.python.org/issue12186 */

static void
_py_free_history_entry(HIST_ENTRY *entry)
{
	UNDO_LIST *undo_list;
	UNDO_LIST *release;

	/* A history entry may have an undo_list attached */
	undo_list = (UNDO_LIST *)free_history_entry(entry);
	while (undo_list) {
		release = undo_list;
		undo_list = undo_list->next;
		if (release->what == UNDO_DELETE)
			free(release->text);
		free(release);
	}
}


/* Remove a history item */

static PyObject *
py_remove_history(PyObject *self, PyObject *args)
{
	int entry_number;
	HIST_ENTRY *entry;

	if (!PyArg_ParseTuple(args, "i:remove_history_item", &entry_number))
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
	_py_free_history_entry(entry);

	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_remove_history,
"remove_history_item(pos) -> None\n\
Remove history item given by its position.");


/* Replace a history item */

static PyObject *
py_replace_history(PyObject *self, PyObject *args)
{
	int entry_number;
	char *line;
	HIST_ENTRY *old_entry;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "iO&:replace_history_item", &entry_number, PyUnicode_StrConverter, &b))
		return NULL;
	line = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "is:replace_history_item", &entry_number, &line))
		return NULL;
#endif
	if (entry_number < 0) {
		PyErr_SetString(PyExc_ValueError,
				"History index cannot be negative");
		goto error;
	}
	old_entry = replace_history_entry(entry_number, line, (void *)NULL);
	if (!old_entry) {
		PyErr_Format(PyExc_ValueError,
			     "No history item at position %d",
			     entry_number);
		goto error;
	}
	/* free memory allocated for the old history entry */
	_py_free_history_entry(old_entry);

	Py_XDECREF(b);
	Py_RETURN_NONE;
  error:
  	Py_XDECREF(b);
	return NULL;
}

PyDoc_STRVAR(doc_replace_history,
"replace_history_item(pos, string) -> None\n\
Replace history item given by its position with string.");


/* Add a line to the history buffer */

static PyObject *
py_add_history(PyObject *self, PyObject *args)
{
	char *line;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if(!PyArg_ParseTuple(args, "O&:add_history", PyUnicode_StrConverter, &b))
		return NULL;
	line = PyBytes_AsString(b);
#else
	if(!PyArg_ParseTuple(args, "s:add_history", &line))
		return NULL;
#endif
	add_history(line);
	Py_XDECREF(b);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_add_history,
"add_history(string) -> None\n\
Add a line to the readline history.");


/* Exported function to get any element of history */

static PyObject *
get_history_item(PyObject *self, PyObject *args)
{
	int idx = 0;
	HIST_ENTRY *hist_ent;

	if (!PyArg_ParseTuple(args, "i:get_history_item", &idx))
		return NULL;
	if ((hist_ent = history_get(history_base + idx)))
		return PyString_FromString(hist_ent->line);
	else {
		Py_RETURN_NONE;
	}
}

PyDoc_STRVAR(doc_get_history_item,
"get_history_item(pos) -> string\n\
Return the current contents of history item at pos.");


/* Exported function to get the entire history as a Python list */

static PyObject *
get_history_list(PyObject *self, PyObject *noarg)
{
	HIST_ENTRY **hist;
	PyObject *list;
	PyObject *s;
	size_t i;

	list = PyList_New(history_length);
	if (list == NULL)
		return NULL;

	hist = history_list();
	if (hist == NULL)
		return list;

	for (i = 0; i < history_length; i++) {
		s = PyString_FromString(hist[i]->line);
		if (s == NULL)
			goto error;
		PyList_SET_ITEM(list, i, s);
	}
	return list;
  error:
	Py_XDECREF(list);
	return NULL;
}

PyDoc_STRVAR(doc_get_history_list,
"get_history_list() -> list\n\
Return the entire history as a Python list. \
Element 0 of the list is the beginning of time.");


/* Exported function returning an iterator over the history */

static PyObject *
get_history_iter(PyObject *self, PyObject *noarg)
{
	return HistoryIterator_New();
}

PyDoc_STRVAR(doc_get_history_iter,
"get_history_iter() -> iterator\n\
Return a forward iterator over the history (oldest to newest).");


/* Exported function returning a reverse iterator over the history */

static PyObject *
get_history_reverse_iter(PyObject *self, PyObject *noarg)
{
	return HistoryReverseIterator_New();
}

PyDoc_STRVAR(doc_get_history_reverse_iter,
"get_history_reverse_iter() -> iterator\n\
Return a reverse iterator over the history (newest to oldest).");


/* Exported function to get current length of history */

static PyObject *
get_current_history_length(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(history_length);
}

PyDoc_STRVAR(doc_get_current_history_length,
"get_current_history_length() -> int\n\
Return the current (not the maximum) length of history.");


/* Exported function to clear the current history */

static PyObject *
py_clear_history(PyObject *self, PyObject *noarg)
/* Reimplemented here to avoid a memory leak in GNU Readline. */
{
	HIST_ENTRY **hist;
	size_t i;

	hist = history_list();
	for (i = 0; i < history_length; i++) {
		_py_free_history_entry(hist[i]);
		hist[i] = (HIST_ENTRY *)NULL;
	}
	history_length = 0;
	clear_history();
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_clear_history,
"clear_history() -> None\n\
Clear the current readline history.");


/* Enable or disable automatic history */

static int should_auto_add_history = 1;


static PyObject *
get_auto_history(PyObject *self, PyObject *noarg)
{
	return PyBool_FromLong(should_auto_add_history);
}

PyDoc_STRVAR(doc_get_auto_history,
"get_auto_history() -> bool\n\
True if automatic history is enabled.");


static PyObject *
set_auto_history(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_auto_history", &value)) {
		return NULL;
	}
	should_auto_add_history = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_auto_history,
"set_auto_history(bool) -> None\n\
Enable or disable automatic history.");


/* Exported function to read the current line buffer */

static PyObject *
get_line_buffer(PyObject *self, PyObject *noarg)
{
	return PyString_FromString(rl_line_buffer);
}

PyDoc_STRVAR(doc_get_line_buffer,
"get_line_buffer() -> string\n\
Return the current contents of the line buffer.");


/* Exported function to insert text into the line buffer */

static PyObject *
insert_text(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:insert_text", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:insert_text", &s))
		return NULL;
#endif
	rl_insert_text(s);
	Py_XDECREF(b);
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
Update the screen to reflect the current \
contents of the line buffer. If ``force`` is True, readline\n\
redisplays the prompt area as well as the line.");


/* <rl.readline>
   https://tiswww.case.edu/php/chet/readline/readline.html#SEC45 */

/* Get/set completion append character */

static PyObject *
get_completion_append_character(PyObject *self, PyObject *noarg)
{
#if (PY_MAJOR_VERSION >= 3)
	return PyUnicode_DECODE_CHAR(rl_completion_append_character);
#else
	if (!rl_completion_append_character)
		return PyString_FromString("");
	return PyString_FromFormat("%c", rl_completion_append_character);
#endif
}

PyDoc_STRVAR(doc_get_completion_append_character,
"get_completion_append_character() -> string\n\
Get the character appended after the current completion.");


static PyObject *
set_completion_append_character(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_completion_append_character", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_completion_append_character", &s))
		return NULL;
#endif
	rl_completion_append_character = (s && *s) ? *s : '\0';
	Py_XDECREF(b);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_append_character,
"set_completion_append_character(string) -> None\n\
Set the character appended after the current completion. \
May only be called from within custom completers.");


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
		return PyString_FromString("");
	return PyString_FromString(rl_completer_quote_characters);
}

PyDoc_STRVAR(doc_get_completer_quote_characters,
"get_completer_quote_characters() -> string\n\
Get list of characters that may be used to quote a substring of the line.");


static PyObject *
set_completer_quote_characters(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_completer_quote_characters", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_completer_quote_characters", &s))
		return NULL;
#endif
	s = strdup(s);
	Py_XDECREF(b);

	if (s) {
		if (rl_completer_quote_characters)
			free((void*)rl_completer_quote_characters);
		rl_completer_quote_characters = s;
		Py_RETURN_NONE;
	}
	else
		return PyErr_NoMemory();
}

PyDoc_STRVAR(doc_set_completer_quote_characters,
"set_completer_quote_characters(string) -> None\n\
Set list of characters that may be used to quote a substring of the line.");


/* Get/set filename quote characters */

static PyObject *
get_filename_quote_characters(PyObject *self, PyObject *noarg)
{
	if (!rl_filename_quote_characters)
		return PyString_FromString("");
	return PyString_FromString(rl_filename_quote_characters);
}

PyDoc_STRVAR(doc_get_filename_quote_characters,
"get_filename_quote_characters() -> string\n\
Get list of characters that cause a filename to be quoted by the completer.");


static PyObject *
set_filename_quote_characters(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_filename_quote_characters", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_filename_quote_characters", &s))
		return NULL;
#endif
	s = strdup(s);
	Py_XDECREF(b);

	if (s) {
		if (rl_filename_quote_characters)
			free((void*)rl_filename_quote_characters);
		rl_filename_quote_characters = s;
		Py_RETURN_NONE;
	}
	else
		return PyErr_NoMemory();
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
set_completion_found_quote(PyObject *self, PyObject *args)
{
	int value;

	if (!PyArg_ParseTuple(args, "i:set_completion_found_quote", &value)) {
		return NULL;
	}
	rl_completion_found_quote = value ? 1 : 0;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_found_quote,
"set_completion_found_quote(bool) -> None\n\
When readline is completing quoted text, it sets this variable to True \
if the word being completed contains any quoting character (including backslashes).");


static PyObject *
get_completion_quote_character(PyObject *self, PyObject *noarg)
{
#if (PY_MAJOR_VERSION >= 3)
	return PyUnicode_DECODE_CHAR(rl_completion_quote_character);
#else
	if (!rl_completion_quote_character)
		return PyString_FromString("");
	return PyString_FromFormat("%c", rl_completion_quote_character);
#endif
}

PyDoc_STRVAR(doc_get_completion_quote_character,
"get_completion_quote_character() -> string\n\
When readline is completing quoted text, it sets this variable to the quoting character found.");


static PyObject *
set_completion_quote_character(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_completion_quote_character", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_completion_quote_character", &s))
		return NULL;
#endif
	rl_completion_quote_character = (s && *s) ? *s : '\0';
	Py_XDECREF(b);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_set_completion_quote_character,
"set_completion_quote_character(string) -> None\n\
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


/* Inhibit completion */

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
If True, completion is disabled and the completion character is inserted \
as any other character.");


/* Filename quoting function */

static char *
on_filename_quoting_function(const char *text, int match_type, char *quote_pointer);

static rl_quote_func_t *default_filename_quoting_function = NULL;


static PyObject *
set_filename_quoting_function(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("filename_quoting_function",
			&global->filename_quoting_function, args);

	rl_filename_quoting_function =
		global->filename_quoting_function ?
		(rl_quote_func_t *)on_filename_quoting_function :
		(rl_quote_func_t *)default_filename_quoting_function;

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
	modulestate *global = PyModule_GetState(self);

	if (global->filename_quoting_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->filename_quoting_function);
	return global->filename_quoting_function;
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
	char quote_char_string[2] = "\0";
	PyObject *single_match = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	single_match = PyBool_FromLong(match_type == SINGLE_MATCH);

	if (quote_pointer && *quote_pointer) {
		quote_char_string[0] = *quote_pointer;
	}
#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->filename_quoting_function, "NON",
				  PyUnicode_DECODE(text), single_match,
				  PyUnicode_DECODE(quote_char_string));
#else
	r = PyObject_CallFunction(global->filename_quoting_function, "sOs",
				  text, single_match, quote_char_string);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = (char*)text;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
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
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Filename dequoting function */

static char *
on_filename_dequoting_function(const char *text, char quote_char);


static PyObject *
set_filename_dequoting_function(PyObject *self, PyObject *args)
{
#if (RL_READLINE_VERSION >= 0x0502)
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("filename_dequoting_function",
			&global->filename_dequoting_function, args);

	rl_filename_dequoting_function =
		global->filename_dequoting_function ?
		(rl_dequote_func_t *)on_filename_dequoting_function : NULL;

	return result;
#else
	Py_RETURN_NONE;
#endif
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
	modulestate *global = PyModule_GetState(self);

	if (global->filename_dequoting_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->filename_dequoting_function);
	return global->filename_dequoting_function;
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
	char quote_char_string[2] = "\0";
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	if (quote_char) {
		quote_char_string[0] = quote_char;
	}
#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->filename_dequoting_function, "NN",
				  PyUnicode_DECODE(text),
				  PyUnicode_DECODE(quote_char_string));
#else
	r = PyObject_CallFunction(global->filename_dequoting_function, "ss",
				  text, quote_char_string);
#endif
	if (r == NULL) {
		result = strdup(text);
		goto error;
	}
	if (r == Py_None) {
		result = strdup(text);
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
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
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	/* We really can't return NULL here, and since this is a hook
	   we can't raise a Python exception either. */
	if (result == NULL) {
		fprintf(stderr, "readline: out of virtual memory\n");
		exit(2);
	}
	return result;
}


/* Char-is-quoted function */

static int
on_char_is_quoted_function(const char *text, int index);


static PyObject *
set_char_is_quoted_function(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("char_is_quoted_function",
			&global->char_is_quoted_function, args);

	rl_char_is_quoted_p =
		global->char_is_quoted_function ?
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
	modulestate *global = PyModule_GetState(self);

	if (global->char_is_quoted_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->char_is_quoted_function);
	return global->char_is_quoted_function;
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
	PyObject *r = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	_py_set_completion_defaults();

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->char_is_quoted_function, "Ni",
				  PyUnicode_DECODE(text),
				  PyUnicode_INDEX(text, index));
#else
	r = PyObject_CallFunction(global->char_is_quoted_function, "si",
	                          text, index);
#endif
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


/* Stock completion functions */

static PyObject *
filename_completion_function(PyObject *self, PyObject *args)
{
	int state;
	char *s;
	char *completion;
	PyObject *r = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&i:filename_completion_function", PyUnicode_StrConverter, &b, &state))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "si:filename_completion_function", &s, &state))
		return NULL;
#endif
	completion = rl_filename_completion_function(s, state);
	Py_XDECREF(b);
	if (!completion)
		Py_RETURN_NONE;
	r = PyString_FromString(completion);
	free(completion);
	return r;
}

PyDoc_STRVAR(doc_filename_completion_function,
"filename_completion_function(text, state) -> string\n\
A built-in generator function for filename completion.");


static PyObject *
username_completion_function(PyObject *self, PyObject *args)
{
	int state;
	char *s;
	char *completion;
	PyObject *r = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&i:username_completion_function", PyUnicode_StrConverter, &b, &state))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "si:username_completion_function", &s, &state))
		return NULL;
#endif
	completion = rl_username_completion_function(s, state);
	Py_XDECREF(b);
	if (!completion)
		Py_RETURN_NONE;
	r = PyString_FromString(completion);
	free(completion);
	return r;
}

PyDoc_STRVAR(doc_username_completion_function,
"username_completion_function(text, state) -> string\n\
A built-in generator function for username completion.");


static PyObject *
py_tilde_expand(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *r = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:tilde_expand", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:tilde_expand", &s))
		return NULL;
#endif
	if (*s == '~') {
		/* tilde_expand aborts when out of memory */
		s = tilde_expand(s);
		r = PyString_FromString(s);
		free(s);
	}
	else
		r = PyString_FromString(s);
	Py_XDECREF(b);
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
		return PyString_FromString("");
	return PyString_FromString(rl_special_prefixes);
}

PyDoc_STRVAR(doc_get_special_prefixes,
"get_special_prefixes() -> string\n\
Characters that are word break characters, but should be left in text \
when it is passed to the completion function.");


static PyObject *
set_special_prefixes(PyObject *self, PyObject *args)
{
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:set_special_prefixes", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:set_special_prefixes", &s))
		return NULL;
#endif
	s = strdup(s);
	Py_XDECREF(b);

	if (s) {
		if (rl_special_prefixes)
			free((void*)rl_special_prefixes);
		rl_special_prefixes = s;
		Py_RETURN_NONE;
	}
	else
		return PyErr_NoMemory();
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


/* Readline version */

static PyObject *
readline_version(PyObject *self, PyObject *noarg)
{
	return PyInt_FromLong(rl_readline_version);
}

PyDoc_STRVAR(doc_readline_version,
"readline_version() -> int\n\
Return the readline library version encoded in an integer. \
The format is ``0xMMmm``, where ``MM`` is the major and ``mm`` \
the minor version number.");


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


static PyObject *
complete_internal(PyObject *self, PyObject *args)
{
	char *what_to_do;
	int result = 1;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:complete_internal", PyUnicode_StrConverter, &b))
		return NULL;
	what_to_do = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:complete_internal", &what_to_do))
		return NULL;
#endif
	result = rl_complete_internal(*what_to_do);
	Py_XDECREF(b);
	return PyInt_FromLong(result);
}

PyDoc_STRVAR(doc_complete_internal,
"complete_internal(what_to_do) -> int\n\
Complete the word at or before the cursor position.");


/* Word-break hook */

static char *
on_completion_word_break_hook(void);

extern char
_rl_find_completion_word(int *fp, int *dp);


static PyObject *
set_completion_word_break_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("completion_word_break_hook",
			&global->completion_word_break_hook, args);

	rl_completion_word_break_hook =
		global->completion_word_break_hook ?
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
	modulestate *global = PyModule_GetState(self);

	if (global->completion_word_break_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->completion_word_break_hook);
	return global->completion_word_break_hook;
}

PyDoc_STRVAR(doc_get_completion_word_break_hook,
"get_completion_word_break_hook() -> function\n\
A function to call when readline is deciding where to separate words for word completion.");


static char *
on_completion_word_break_hook(void)
/* Memory returned by this function is never freed. We must keep
   it around in a static pointer and free it on the next call. */
{
	char *result = NULL;
	char *s = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;
	int start, end;
	static char *last = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	_py_set_completion_defaults();

	/* Determine word boundaries */
	end = rl_point;
	if (rl_point) {
		/* Unhook ourselves to avoid infinite recursion */
		rl_completion_word_break_hook = NULL;
		_rl_find_completion_word(NULL, NULL);
		rl_completion_word_break_hook =
			(rl_cpvfunc_t *)on_completion_word_break_hook;
	}
	start = rl_point;
	rl_point = end;

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->completion_word_break_hook, "ii",
				  PyUnicode_INDEX(rl_line_buffer, start),
				  PyUnicode_INDEX(rl_line_buffer, end));
#else
	r = PyObject_CallFunction(global->completion_word_break_hook, "ii",
	                          start, end);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = NULL;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
		if (s == NULL)
			goto error;
		result = strdup(s);
		if (last != NULL)
			free(last);
		last = result;
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Directory rewrite hook */

static int
on_directory_rewrite_hook(char **directory);


static PyObject *
set_directory_rewrite_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("directory_rewrite_hook",
			&global->directory_rewrite_hook, args);

	rl_directory_rewrite_hook =
		global->directory_rewrite_hook ?
		(rl_icppfunc_t *)on_directory_rewrite_hook : NULL;

	return result;
}

PyDoc_STRVAR(doc_set_directory_rewrite_hook,
"set_directory_rewrite_hook([function]) -> None\n\
This function is used to prepare the director name passed to ``opendir()`` during filename completion. \
The function is called as ``function(dirname)`` and should return a new directory name or \
None to indicate no change. At the least, the function must perform all necessary \
dequoting.");


static PyObject *
get_directory_rewrite_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->directory_rewrite_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->directory_rewrite_hook);
	return global->directory_rewrite_hook;
}

PyDoc_STRVAR(doc_get_directory_rewrite_hook,
"get_directory_rewrite_hook() -> function\n\
Get the current directory rewrite hook function.");


static int
on_directory_rewrite_hook(char **directory)
{
	int result = 0;
	char *s = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->directory_rewrite_hook, "N",
				  PyUnicode_DECODE(*directory));
#else
	r = PyObject_CallFunction(global->directory_rewrite_hook, "s",
				  *directory);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_FS_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
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
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Directory completion hook */

static int
on_directory_completion_hook(char **directory);


static PyObject *
set_directory_completion_hook(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("directory_completion_hook",
			&global->directory_completion_hook, args);

	rl_directory_completion_hook =
		global->directory_completion_hook ?
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
	modulestate *global = PyModule_GetState(self);

	if (global->directory_completion_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->directory_completion_hook);
	return global->directory_completion_hook;
}

PyDoc_STRVAR(doc_get_directory_completion_hook,
"get_directory_completion_hook() -> function\n\
Get the current directory completion hook function.");


static int
on_directory_completion_hook(char **directory)
{
	int result = 0;
	char *s = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->directory_completion_hook, "N",
				  PyUnicode_DECODE(*directory));
#else
	r = PyObject_CallFunction(global->directory_completion_hook, "s",
				  *directory);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
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
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Filename rewrite hook */

static char *
on_filename_rewrite_hook(const char *text, int num_bytes);


static PyObject *
set_filename_rewrite_hook(PyObject *self, PyObject *args)
{
#if (RL_READLINE_VERSION >= 0x0601)
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("filename_rewrite_hook",
			&global->filename_rewrite_hook, args);

	rl_filename_rewrite_hook =
		global->filename_rewrite_hook ?
		(rl_dequote_func_t *)on_filename_rewrite_hook : NULL;

	return result;
#else
	Py_RETURN_NONE;
#endif
}

PyDoc_STRVAR(doc_set_filename_rewrite_hook,
"set_filename_rewrite_hook([function]) -> None\n\
This function is called for every filename before it is compared against the completion word. \
The function is called as ``function(filename)`` and should return a new filename or \
None to indicate no change.");


static PyObject *
get_filename_rewrite_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->filename_rewrite_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->filename_rewrite_hook);
	return global->filename_rewrite_hook;
}

PyDoc_STRVAR(doc_get_filename_rewrite_hook,
"get_filename_rewrite_hook() -> function\n\
Get the current filename rewrite hook function.");


static char *
on_filename_rewrite_hook(const char *text, int num_bytes)
/* This function must return new memory on success and the
   passed-in 'text' pointer to indicate no change. */
{
	char *result = (char*)text;
	char *s = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->filename_rewrite_hook, "N",
				  PyUnicode_FS_DECODE(text));
#else
	r = PyObject_CallFunction(global->filename_rewrite_hook, "s",
				  text);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = (char *)text;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
		if (s == NULL)
			goto error;
		s = strdup(s);
		if (s != NULL)
			result = s;
	}
	Py_DECREF(r);
	goto done;
  error:
	PyErr_Clear();
	Py_XDECREF(r);
  done:
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Filename stat hook */

static int
on_filename_stat_hook(char **directory);


static PyObject *
set_filename_stat_hook(PyObject *self, PyObject *args)
{
#if (RL_READLINE_VERSION >= 0x0603)
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("filename_stat_hook",
			&global->filename_stat_hook, args);

	rl_filename_stat_hook =
		global->filename_stat_hook ?
		(rl_icppfunc_t *)on_filename_stat_hook : NULL;

	return result;
#else
	Py_RETURN_NONE;
#endif
}

PyDoc_STRVAR(doc_set_filename_stat_hook,
"set_filename_stat_hook([function]) -> None\n\
This function is used to prepare the filename passed to ``stat()`` during match display. \
The function is called as ``function(filename)`` and should return a new filename name or \
None to indicate no change.");


static PyObject *
get_filename_stat_hook(PyObject *self, PyObject *noargs)
{
	modulestate *global = PyModule_GetState(self);

	if (global->filename_stat_hook == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->filename_stat_hook);
	return global->filename_stat_hook;
}

PyDoc_STRVAR(doc_get_filename_stat_hook,
"get_filename_stat_hook() -> function\n\
Get the current filename stat hook function.");


static int
on_filename_stat_hook(char **directory)
{
	int result = 0;
	char *s = NULL;
	PyObject *r = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->filename_stat_hook, "N",
				  PyUnicode_DECODE(*directory));
#else
	r = PyObject_CallFunction(global->filename_stat_hook, "s",
				  *directory);
#endif
	if (r == NULL)
		goto error;
	if (r == Py_None) {
		result = 0;
	}
	else {
#if (PY_MAJOR_VERSION >= 3)
		b = PyUnicode_FS_ENCODE(r);
		if (b != NULL)
			s = PyBytes_AsString(b);
#else
		s = PyString_AsString(r);
#endif
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
	Py_XDECREF(b);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* Replace line buffer contents */

static PyObject *
replace_line(PyObject *self, PyObject *args)
{
	char *s = NULL;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:replace_line", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:replace_line", &s))
		return NULL;
#endif
	if (s) {
		rl_replace_line(s, 0);
		/* Move rl_point to end of line */
		rl_point = rl_end;
	}
	Py_XDECREF(b);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_replace_line,
"replace_line(string) -> None\n\
Replace the line buffer contents with string.");


/* Read a key (from the keyboard) */

static PyObject *
read_key(PyObject *self, PyObject *noargs)
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

#if (PY_MAJOR_VERSION >= 3)
	return PyUnicode_DECODE_CHAR(c);
#else
	return PyString_FromFormat("%c", c);
#endif
}

PyDoc_STRVAR(doc_read_key,
"read_key() -> string\n\
Read a key from readline's input stream, typically the keyboard. \
Returns characters inserted with :func:`stuff_char` before starting to read \
from the stream.");


/* Stuff a character into the input stream */

static PyObject *
stuff_char(PyObject *self, PyObject *args)
{
	char *s = NULL;
	int r = 0;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&:stuff_char", PyUnicode_StrConverter, &b))
		return NULL;
	s = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "s:stuff_char", &s))
		return NULL;
#endif
	if (s && *s)
		r = rl_stuff_char(*s);
	Py_XDECREF(b);
	return PyBool_FromLong(r);
}

PyDoc_STRVAR(doc_stuff_char,
"stuff_char(string) -> bool\n\
Insert a character into readline's input stream. \
Returns True if the insert was successful.");


/* Display match list function */

static PyObject*
display_match_list(PyObject *self, PyObject *args)
{
	char *substitution = NULL;
	PyObject *matches = NULL;
	Py_ssize_t num_matches = 0;
	int max_length = 0;
	char **strings = NULL;
	char *s;
	PyObject *b = NULL;

#if (PY_MAJOR_VERSION >= 3)
	if (!PyArg_ParseTuple(args, "O&Oi:display_match_list",
			      PyUnicode_StrConverter, &b, &matches, &max_length))
		return NULL;
	substitution = PyBytes_AsString(b);
#else
	if (!PyArg_ParseTuple(args, "sOi:display_match_list",
			      &substitution, &matches, &max_length))
		return NULL;
#endif
	num_matches = PyList_Size(matches);
	if (num_matches == -1)
		goto error;

	strings = StringArray_FromPyList(matches);
	if (strings == NULL)
		goto error;

	s = strdup(substitution);
	if (s == NULL) {
		PyErr_NoMemory();
		goto error;
	}

	/* Put the substitution back into the list at position 0 */
	if (StringArray_Insert(&strings, 0, s) == -1)
		goto error;

	/* Temporarily unset callback state so the pager works */
	if (RL_ISSTATE(RL_STATE_CALLBACK)) {
		RL_UNSETSTATE(RL_STATE_CALLBACK);
		rl_display_match_list(strings, num_matches, max_length);
		RL_SETSTATE(RL_STATE_CALLBACK);
	}
	else
		rl_display_match_list(strings, num_matches, max_length);

	/* Clear KeyboardInterrupt */
	if (PyErr_CheckSignals() == -1 &&
	    PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
		PyErr_Clear();

	Py_XDECREF(b);
	StringArray_Free(strings);
	Py_RETURN_NONE;
  error:
	Py_XDECREF(b);
	StringArray_Free(strings);
	return NULL;
}

PyDoc_STRVAR(doc_display_match_list,
"display_match_list(substitution, matches, longest_match_length) -> None\n\
Display a list of matches in columnar format on readline's output stream.");


/* Ignore some completions function */

static int
on_ignore_some_completions_function(char **directory);


static PyObject *
set_ignore_some_completions_function(PyObject *self, PyObject *args)
{
	modulestate *global = PyModule_GetState(self);

	PyObject *result = set_hook("ignore_some_completions_function",
			&global->ignore_some_completions_function, args);

	rl_ignore_some_completions_function =
		global->ignore_some_completions_function ?
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
	modulestate *global = PyModule_GetState(self);

	if (global->ignore_some_completions_function == NULL) {
		Py_RETURN_NONE;
	}
	Py_INCREF(global->ignore_some_completions_function);
	return global->ignore_some_completions_function;
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
	modulestate *global = PyModule_GetState(readline_module());

	m = PyList_FromStringArray(matches+1);
	if (m == NULL)
		goto error;

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->ignore_some_completions_function, "NO",
				  PyUnicode_DECODE(matches[0]), m);
#else
	r = PyObject_CallFunction(global->ignore_some_completions_function, "sO",
				  matches[0], m);
#endif
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

		strings = StringArray_FromPyList(r);
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


/* History stifling */

PyObject *
get_history_max_entries(PyObject *self, PyObject *noargs)
{
	return PyInt_FromLong(history_max_entries);
}

PyDoc_STRVAR(doc_get_history_max_entries,
"get_history_max_entries() -> int\n\
Return the current history size limit.");


PyObject *
py_stifle_history(PyObject *self, PyObject *args)
{
	int max;

	if (!PyArg_ParseTuple(args, "i:stifle_history", &max))
		return NULL;
	stifle_history(max);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_stifle_history,
"stifle_history(max_entries) -> None\n\
Limit the history size to ``max_entries`` entries.");


PyObject *
py_unstifle_history(PyObject *self, PyObject *noargs)
{
	return PyInt_FromLong(unstifle_history());
}

PyDoc_STRVAR(doc_unstifle_history,
"unstifle_history() -> int\n\
Remove the history size limit.");


PyObject *
py_history_is_stifled(PyObject *self, PyObject *noargs)
{
	return PyBool_FromLong(history_is_stifled());
}

PyDoc_STRVAR(doc_history_is_stifled,
"history_is_stifled() -> bool\n\
True if a history size limit is set.");


/* Default display matches hook */

static int
get_y_or_n(void)
/* Readline's implementation of get_y_or_n() is private. */
{
	int c;

	for (;;) {
		RL_SETSTATE(RL_STATE_MOREINPUT);
		c = rl_read_key();
		RL_UNSETSTATE(RL_STATE_MOREINPUT);

		if (c == 'y' || c == 'Y' || c == ' ')
			return 1;
		if (c == 'n' || c == 'N' || c == RUBOUT)
			return 0;
		rl_ding();
	}
}


static void
default_display_matches_hook(char **matches, int num_matches, int max_length)
/* Readline's implementation does not read from the keyboard in
   callback mode. */
{
	int completion_y_or_n = 1;

	if (rl_completion_query_items > 0 && num_matches >= rl_completion_query_items)
	{
		rl_crlf();
		fprintf(rl_outstream, "Display all %d possibilities? (y or n)", num_matches);
		fflush(rl_outstream);

		/* Temporarily unset callback state */
		if (RL_ISSTATE(RL_STATE_CALLBACK)) {
			RL_UNSETSTATE(RL_STATE_CALLBACK);
			completion_y_or_n = get_y_or_n();
			RL_SETSTATE(RL_STATE_CALLBACK);
		}
		else
			completion_y_or_n = get_y_or_n();
#ifdef WITH_THREAD
		PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
		/* Clear KeyboardInterrupt */
		if (PyErr_CheckSignals() == -1 &&
		    PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
			PyErr_Clear();
#ifdef WITH_THREAD
		PyGILState_Release(gilstate);
#endif
		if (completion_y_or_n == 0) {
			rl_crlf();
			rl_forced_update_display();
			rl_display_fixed = 1;
			return;
		}
	}

	/* Temporarily unset callback state so the pager works */
	if (RL_ISSTATE(RL_STATE_CALLBACK)) {
		RL_UNSETSTATE(RL_STATE_CALLBACK);
		rl_display_match_list(matches, num_matches, max_length);
		RL_SETSTATE(RL_STATE_CALLBACK);
	}
	else
		rl_display_match_list(matches, num_matches, max_length);

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	/* Clear KeyboardInterrupt */
	if (PyErr_CheckSignals() == -1 &&
	    PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
		PyErr_Clear();
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	rl_forced_update_display();
	rl_display_fixed = 1;
}

/* </rl.readline> */


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
	{"append_history_file", append_history_file,
	 METH_VARARGS, doc_append_history_file},
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
	{"set_pre_input_hook", set_pre_input_hook,
	 METH_VARARGS, doc_set_pre_input_hook},
	{"clear_history", py_clear_history, METH_NOARGS, doc_clear_history},
	{"set_auto_history", set_auto_history, METH_VARARGS, doc_set_auto_history},

	/* <rl.readline> */
	{"get_completion_append_character", get_completion_append_character,
	 METH_NOARGS, doc_get_completion_append_character},
	{"set_completion_append_character", set_completion_append_character,
	 METH_VARARGS, doc_set_completion_append_character},
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
	{"set_completion_found_quote", set_completion_found_quote,
	 METH_VARARGS, doc_set_completion_found_quote},
	{"get_completion_quote_character", get_completion_quote_character,
	 METH_NOARGS, doc_get_completion_quote_character},
	{"set_completion_quote_character", set_completion_quote_character,
	 METH_VARARGS, doc_set_completion_quote_character},
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
	{"set_begidx", set_begidx, METH_VARARGS, doc_set_begidx},
	{"set_endidx", set_endidx, METH_VARARGS, doc_set_endidx},
	{"set_completion_type", set_completion_type,
	 METH_VARARGS, doc_set_completion_type},
	{"get_pre_input_hook", get_pre_input_hook,
	 METH_NOARGS, doc_get_pre_input_hook},
	{"get_inhibit_completion", get_inhibit_completion,
	 METH_NOARGS, doc_get_inhibit_completion},
	{"set_inhibit_completion", set_inhibit_completion,
	 METH_VARARGS, doc_set_inhibit_completion},
	{"get_completion_word_break_hook", get_completion_word_break_hook,
	 METH_NOARGS, doc_get_completion_word_break_hook},
	{"set_completion_word_break_hook", set_completion_word_break_hook,
	 METH_VARARGS, doc_set_completion_word_break_hook},
	{"get_directory_rewrite_hook", get_directory_rewrite_hook,
	 METH_NOARGS, doc_get_directory_rewrite_hook},
	{"set_directory_rewrite_hook", set_directory_rewrite_hook,
	 METH_VARARGS, doc_set_directory_rewrite_hook},
	{"get_directory_completion_hook", get_directory_completion_hook,
	 METH_NOARGS, doc_get_directory_completion_hook},
	{"set_directory_completion_hook", set_directory_completion_hook,
	 METH_VARARGS, doc_set_directory_completion_hook},
	{"get_filename_rewrite_hook", get_filename_rewrite_hook,
	 METH_NOARGS, doc_get_filename_rewrite_hook},
	{"set_filename_rewrite_hook", set_filename_rewrite_hook,
	 METH_VARARGS, doc_set_filename_rewrite_hook},
	{"get_filename_stat_hook", get_filename_stat_hook,
	 METH_NOARGS, doc_get_filename_stat_hook},
	{"set_filename_stat_hook", set_filename_stat_hook,
	 METH_VARARGS, doc_set_filename_stat_hook},
	{"get_ignore_some_completions_function", get_ignore_some_completions_function,
	 METH_NOARGS, doc_get_ignore_some_completions_function},
	{"set_ignore_some_completions_function", set_ignore_some_completions_function,
	 METH_VARARGS, doc_set_ignore_some_completions_function},
	{"tilde_expand", py_tilde_expand, METH_VARARGS, doc_tilde_expand},
	{"replace_line", replace_line, METH_VARARGS, doc_replace_line},
	{"read_key", read_key, METH_NOARGS, doc_read_key},
	{"stuff_char", stuff_char, METH_VARARGS, doc_stuff_char},
	{"display_match_list", display_match_list,
	 METH_VARARGS, doc_display_match_list},
	{"get_rl_point", get_rl_point, METH_NOARGS, doc_get_rl_point},
	{"get_rl_end", get_rl_end, METH_NOARGS, doc_get_rl_end},
	{"complete_internal", complete_internal,
	 METH_VARARGS, doc_complete_internal},
	{"readline_version", readline_version,
	 METH_NOARGS, doc_readline_version},
	{"get_history_max_entries", get_history_max_entries,
	 METH_NOARGS, doc_get_history_max_entries},
	{"stifle_history", py_stifle_history,
	 METH_VARARGS, doc_stifle_history},
	{"unstifle_history", py_unstifle_history,
	 METH_NOARGS, doc_unstifle_history},
	{"history_is_stifled", py_history_is_stifled,
	 METH_NOARGS, doc_history_is_stifled},
	{"get_history_list", get_history_list,
	 METH_NOARGS, doc_get_history_list},
	{"get_history_iter", get_history_iter,
	 METH_NOARGS, doc_get_history_iter},
	{"get_history_reverse_iter", get_history_reverse_iter,
	 METH_NOARGS, doc_get_history_reverse_iter},
	{"get_auto_history", get_auto_history, METH_NOARGS, doc_get_auto_history},
	/* </rl.readline> */

	{0, 0}
};


/* C function to call the Python hooks. */

static int
on_hook(PyObject *func)
{
	int result = 0;
	if (func != NULL) {
		PyObject *r;
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
		return result;
	}
	return result;
}

static int
on_startup_hook(void)
{
#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	int result = on_hook(global->startup_hook);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}

static int
on_pre_input_hook(void)
{
#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	int result = on_hook(global->pre_input_hook);
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* C function to call the Python completion_display_matches_hook. */

static void
on_completion_display_matches_hook(char **matches,
				   int num_matches, int max_length)
{
	PyObject *m=NULL, *r=NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	m = PyList_FromStringArray(matches+1);
	if (m == NULL)
		goto error;

#if (PY_MAJOR_VERSION >= 3)
	r = PyObject_CallFunction(global->completion_display_matches_hook, "NOi",
				  PyUnicode_DECODE(matches[0]), m, max_length);
#else
	r = PyObject_CallFunction(global->completion_display_matches_hook, "sOi",
				  matches[0], m, max_length);
#endif
	Py_CLEAR(m);

	if (r == NULL ||
	    (r != Py_None && PyInt_AsLong(r) == -1 && PyErr_Occurred())) {
		goto error;
	}
	Py_CLEAR(r);

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
	char *s = NULL;
	PyObject *b = NULL;

#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	modulestate *global = PyModule_GetState(readline_module());

	if (global->completer != NULL) {
		PyObject *r;
		rl_attempted_completion_over = 1;
#if (PY_MAJOR_VERSION >= 3)
		r = PyObject_CallFunction(global->completer, "Ni", PyUnicode_DECODE(text), state);
#else
		r = PyObject_CallFunction(global->completer, "si", text, state);
#endif
		if (r == NULL)
			goto error;
		if (r == Py_None) {
			result = NULL;
		}
		else {
#if (PY_MAJOR_VERSION >= 3)
			b = PyUnicode_ENCODE(r);
			if (b != NULL)
				s = PyBytes_AsString(b);
#else
			s = PyString_AsString(r);
#endif
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
	  	Py_XDECREF(b);
	}
#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return result;
}


/* A more flexible constructor that saves "begidx" and "endidx"
 * before calling the normal completer */

static char **
flex_completer(char *text, int start, int end)
{
#ifdef WITH_THREAD
	PyGILState_STATE gilstate = PyGILState_Ensure();
#endif
	_py_set_completion_defaults();

#if (PY_MAJOR_VERSION >= 3)
	begidx = PyUnicode_INDEX(rl_line_buffer, start);
	endidx = PyUnicode_INDEX(rl_line_buffer, end);
#else
	begidx = start;
	endidx = end;
#endif

#ifdef WITH_THREAD
	PyGILState_Release(gilstate);
#endif
	return completion_matches(text, *on_completion);
}


/* Helper to reset completion variables. Sadly no hook. */

static void
_py_set_completion_defaults(void)
{
	begidx = endidx = 0;

#if (RL_READLINE_VERSION < 0x0600)
	rl_completion_append_character = ' ';
#endif
}


/* SIGWINCH handler */

static volatile sig_atomic_t sigwinch_received = 0;
static PyOS_sighandler_t sigwinch_ohandler = NULL;


static void
readline_sigwinch_handler(int signum)
{
	sigwinch_received = 1;

	if (sigwinch_ohandler && sigwinch_ohandler != SIG_IGN && sigwinch_ohandler != SIG_DFL)
		sigwinch_ohandler(signum);

#ifndef HAVE_SIGACTION
	/* If the handler was installed with signal() rather than sigaction(),
	   we need to reinstall it. */
	sigwinch_ohandler = PyOS_setsig(SIGWINCH, readline_sigwinch_handler);
#endif
}


/* Helper to initialize GNU readline properly. */

static int
setup_readline(PyObject *module)
{
#ifdef SAVE_LOCALE
	char *saved_locale = strdup(setlocale(LC_CTYPE, NULL));
	if (!saved_locale)
		return -1;
#endif
	/* Support $if <readline_name> sections in .inputrc */
	rl_readline_name = getenv("RL_READLINE_NAME");
	if (rl_readline_name == NULL)
		rl_readline_name = "python";
#if defined(PYOS_OS2) && defined(PYCC_GCC)
	/* Allow $if term= in .inputrc to work */
	rl_terminal_name = getenv("TERM");
#endif
	/* Initialize history variables */
	using_history();

	/* Force rebind of TAB to insert-tab */
	rl_bind_key('\t', rl_insert);
	/* Bind both ESC-TAB and ESC-ESC to the completion function */
	rl_bind_key_in_map ('\t', rl_complete, emacs_meta_keymap);
	rl_bind_key_in_map ('\033', rl_complete, emacs_meta_keymap);
	/* Set up signal handler for window resize */
	sigwinch_ohandler = PyOS_setsig(SIGWINCH, readline_sigwinch_handler);
	/* Set our hook functions */
	rl_startup_hook = NULL;
	rl_pre_input_hook = NULL;
	/* Set our completion function */
	rl_attempted_completion_function = (rl_completion_func_t *)flex_completer;
	/* Set Python word break characters */
	rl_completer_word_break_characters =
		strdup(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>/?");
		/* All nonalphanums except '.' */
	/* Set the default display matches hook */
	rl_completion_display_matches_hook = default_display_matches_hook;
	/* Save a reference to the default filename quoting function */
	default_filename_quoting_function = rl_filename_quoting_function;
	/* Initialize module state */
	readline_init_state(module);
	/* Reset completion variables */
	_py_set_completion_defaults();

	if (!isatty(STDOUT_FILENO)) {
		/* Issue #19884: stdout is no a terminal. Disable meta modifier
		   keys to not write the ANSI sequence "\033[1034h" into stdout. On
		   terminals supporting 8 bit characters like TERM=xterm-256color
		   (which is now the default Fedora since Fedora 18), the meta key is
		   used to enable support of 8 bit characters (ANSI sequence
		   "\033[1034h"). */
		rl_variable_bind("enable-meta-key", "off");
	}

	/* Initialize (allows .inputrc to override) */
	rl_initialize();

	RESTORE_LOCALE(saved_locale)
	return 0;
}


/* Wrapper around GNU readline that handles signals differently. */

#if defined(HAVE_SELECT)

static	char *completed_input_string;
static void
rlhandler(char *text)
{
	completed_input_string = text;
	rl_callback_handler_remove();
}


static char *
readline_until_enter_or_signal(const char *prompt, int *signal)
{
	char * not_done_reading = "";
	fd_set selectset;

	*signal = 0;
	rl_catch_signals = 0;

	rl_callback_handler_install (prompt, rlhandler);
	FD_ZERO(&selectset);

	completed_input_string = not_done_reading;

	while (completed_input_string == not_done_reading) {
		int has_input = 0, saved_errno = 0;

		while (!has_input) {
			struct timeval timeout = {0, 100000}; /* 0.1 seconds */

			/* [Bug #1552726] Only limit the pause if an input hook has been
			   defined.  */
			struct timeval *timeoutp = NULL;
			if (PyOS_InputHook)
				timeoutp = &timeout;
			/* Update readline's view of the window size after SIGWINCH */
			if (sigwinch_received) {
				sigwinch_received = 0;
				rl_resize_terminal();
			}
			FD_SET(fileno(rl_instream), &selectset);
			/* select resets selectset if no input was available */
			has_input = select(fileno(rl_instream) + 1, &selectset,
					   NULL, NULL, timeoutp);
			saved_errno = errno;
			if (PyOS_InputHook)
				PyOS_InputHook();
		}

		if (has_input > 0) {
			rl_callback_read_char();
		}
		else if (saved_errno == EINTR) {
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
#if (RL_READLINE_VERSION >= 0x0700)
				rl_callback_sigcleanup();
#endif
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
readline_until_enter_or_signal(const char *prompt, int *signal)
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
#endif /* defined(HAVE_SELECT) */


#if (PY_VERSION_HEX < 0x03040000)
static char *
call_readline(FILE *sys_stdin, FILE *sys_stdout, char *prompt)
#else
static char *
call_readline(FILE *sys_stdin, FILE *sys_stdout, const char *prompt)
#endif
{
	size_t n;
	char *p, *q;
	int signal;

#ifdef SAVE_LOCALE
	char *saved_locale = strdup(setlocale(LC_CTYPE, NULL));
	if (!saved_locale)
		return (void*)PyErr_NoMemory();
	_Py_SetLocaleFromEnv(LC_CTYPE);
#endif

	if (sys_stdin != rl_instream || sys_stdout != rl_outstream) {
		rl_instream = sys_stdin;
		rl_outstream = sys_stdout;
		rl_prep_terminal (1);
	}

	p = readline_until_enter_or_signal(prompt, &signal);

	/* we got an interrupt signal */
	if (signal) {
		RESTORE_LOCALE(saved_locale)
		return NULL;
	}

	/* We got an EOF, return a empty string. */
	if (p == NULL) {
		p = PyMem_RawMalloc(1);
		if (p != NULL)
			*p = '\0';
		RESTORE_LOCALE(saved_locale)
		return p;
	}

	/* we have a valid line */
	n = strlen(p);
	if (should_auto_add_history && n > 0) {
		HIST_ENTRY *hist_ent;
		char *line;
		if (history_length > 0) {
			hist_ent = history_get(history_base + history_length - 1);
			line = hist_ent ? hist_ent->line : "";
		}
		else
			line = "";
		if (strcmp(p, line) != 0)
			add_history(p);
	}
	/* Copy the malloc'ed buffer into a PyMem_Malloc'ed one and
	   release the original. */
	q = p;
	p = PyMem_RawMalloc(n+2);
	if (p != NULL) {
		memcpy(p, q, n);
		p[n] = '\n';
		p[n+1] = '\0';
	}
	free(q);
	RESTORE_LOCALE(saved_locale)
	return p;
}


/* Initialize the module */

PyDoc_STRVAR(doc_module,
"Importing this module enables command line editing using GNU Readline.");

#if (PY_MAJOR_VERSION >= 3)
struct PyModuleDef readlinemodule = {
	PyModuleDef_HEAD_INIT,
	"readline",
	doc_module,
	sizeof(modulestate),
	readline_methods,
	NULL,
	readline_traverse,
	readline_clear,
	readline_free
};

PyMODINIT_FUNC
PyInit_readline(void)
{
	PyObject *m;

	m = PyModule_Create(&readlinemodule);
	if (m == NULL)
		return NULL;

	PyOS_ReadlineFunctionPointer = call_readline;

	if (setup_readline(m) < 0) {
		PyErr_NoMemory();
		Py_DECREF(m);
		return NULL;
	}
	return m;
}
#else
PyMODINIT_FUNC
initreadline(void)
{
	PyObject *m;

	m = Py_InitModule4("readline", readline_methods, doc_module,
			   (PyObject *)NULL, PYTHON_API_VERSION);
	if (m == NULL)
		return;

	PyOS_ReadlineFunctionPointer = call_readline;

	if (setup_readline(m) < 0) {
		PyErr_NoMemory();
		Py_DECREF(m);
	}
}
#endif


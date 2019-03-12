#include "Python.h"
#include "modulestate.h"

#if (PY_MAJOR_VERSION < 3)
readlinestate _py2_readlinestate;
#endif


void readline_init_state(PyObject *module)
{
	readlinestate *global = PyModule_GetState(module);
	global->completer = NULL;
	global->startup_hook = NULL;
	global->pre_input_hook = NULL;
	global->completion_word_break_hook = NULL;
	global->char_is_quoted_function = NULL;
	global->filename_quoting_function = NULL;
	global->filename_dequoting_function = NULL;
	global->directory_completion_hook = NULL;
	global->ignore_some_completions_function = NULL;
	global->completion_display_matches_hook = NULL;
	global->directory_rewrite_hook = NULL;
	global->filename_rewrite_hook = NULL;
	global->filename_stat_hook = NULL;
}


#if (PY_MAJOR_VERSION >= 3)

int readline_traverse(PyObject *module, visitproc visit, void *arg)
{
	readlinestate *global = PyModule_GetState(module);
	if (global == NULL)
		return 0;

	Py_VISIT(global->completer);
	Py_VISIT(global->startup_hook);
	Py_VISIT(global->pre_input_hook);
	Py_VISIT(global->completion_word_break_hook);
	Py_VISIT(global->char_is_quoted_function);
	Py_VISIT(global->filename_quoting_function);
	Py_VISIT(global->filename_dequoting_function);
	Py_VISIT(global->directory_completion_hook);
	Py_VISIT(global->ignore_some_completions_function);
	Py_VISIT(global->completion_display_matches_hook);
	Py_VISIT(global->directory_rewrite_hook);
	Py_VISIT(global->filename_rewrite_hook);
	Py_VISIT(global->filename_stat_hook);
	return 0;
}


int readline_clear(PyObject *module)
{
	readlinestate *global = PyModule_GetState(module);
	if (global == NULL)
		return 0;

	Py_CLEAR(global->completer);
	Py_CLEAR(global->startup_hook);
	Py_CLEAR(global->pre_input_hook);
	Py_CLEAR(global->completion_word_break_hook);
	Py_CLEAR(global->char_is_quoted_function);
	Py_CLEAR(global->filename_quoting_function);
	Py_CLEAR(global->filename_dequoting_function);
	Py_CLEAR(global->directory_completion_hook);
	Py_CLEAR(global->ignore_some_completions_function);
	Py_CLEAR(global->completion_display_matches_hook);
	Py_CLEAR(global->directory_rewrite_hook);
	Py_CLEAR(global->filename_rewrite_hook);
	Py_CLEAR(global->filename_stat_hook);
	return 0;
}


void readline_free(void *module)
{
	readline_clear((PyObject *) module);
}

#endif /* Python 3 */

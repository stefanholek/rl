#include "Python.h"
#include "modulestate.h"

#if (PY_MAJOR_VERSION < 3)
readlinestate _py2_readlinestate;
#endif


void readline_init_state(PyObject *module)
{
	readlinestate *modstate = readline_state(module);
	modstate->completer = NULL;
	modstate->startup_hook = NULL;
	modstate->pre_input_hook = NULL;
	modstate->completion_word_break_hook = NULL;
	modstate->char_is_quoted_function = NULL;
	modstate->filename_quoting_function = NULL;
	modstate->filename_dequoting_function = NULL;
	modstate->directory_completion_hook = NULL;
	modstate->ignore_some_completions_function = NULL;
	modstate->completion_display_matches_hook = NULL;
	modstate->directory_rewrite_hook = NULL;
	modstate->filename_rewrite_hook = NULL;
	modstate->filename_stat_hook = NULL;
}


#if (PY_MAJOR_VERSION >= 3)

int readline_traverse(PyObject *module, visitproc visit, void *arg)
{
	readlinestate *modstate = readline_state(module);
	Py_VISIT(modstate->completer);
	Py_VISIT(modstate->startup_hook);
	Py_VISIT(modstate->pre_input_hook);
	Py_VISIT(modstate->completion_word_break_hook);
	Py_VISIT(modstate->char_is_quoted_function);
	Py_VISIT(modstate->filename_quoting_function);
	Py_VISIT(modstate->filename_dequoting_function);
	Py_VISIT(modstate->directory_completion_hook);
	Py_VISIT(modstate->ignore_some_completions_function);
	Py_VISIT(modstate->completion_display_matches_hook);
	Py_VISIT(modstate->directory_rewrite_hook);
	Py_VISIT(modstate->filename_rewrite_hook);
	Py_VISIT(modstate->filename_stat_hook);
	return 0;
}


int readline_clear(PyObject *module)
{
	readlinestate *modstate = readline_state(module);
	Py_CLEAR(modstate->completer);
	Py_CLEAR(modstate->startup_hook);
	Py_CLEAR(modstate->pre_input_hook);
	Py_CLEAR(modstate->completion_word_break_hook);
	Py_CLEAR(modstate->char_is_quoted_function);
	Py_CLEAR(modstate->filename_quoting_function);
	Py_CLEAR(modstate->filename_dequoting_function);
	Py_CLEAR(modstate->directory_completion_hook);
	Py_CLEAR(modstate->ignore_some_completions_function);
	Py_CLEAR(modstate->completion_display_matches_hook);
	Py_CLEAR(modstate->directory_rewrite_hook);
	Py_CLEAR(modstate->filename_rewrite_hook);
	Py_CLEAR(modstate->filename_stat_hook);
	return 0;
}


void readline_free(void *module)
{
	readline_clear((PyObject *) module);
}

#endif /* Python 3 */

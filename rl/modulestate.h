#ifndef __MODULESTATE_H__
#define __MODULESTATE_H__

#include "Python.h"

/* Module state (PEP 3121) */

typedef struct {
	PyObject *completer;
	PyObject *startup_hook;
	PyObject *pre_input_hook;
	PyObject *completion_word_break_hook;
	PyObject *char_is_quoted_function;
	PyObject *filename_quoting_function;
	PyObject *filename_dequoting_function;
	PyObject *directory_completion_hook;
	PyObject *ignore_some_completions_function;
	PyObject *completion_display_matches_hook;
	PyObject *directory_rewrite_hook;
	PyObject *filename_rewrite_hook;
	PyObject *filename_stat_hook;
} readlinestate;

typedef readlinestate modulestate;

void readline_init_state(PyObject *module);

#if (PY_MAJOR_VERSION >= 3)
	extern struct PyModuleDef readlinemodule;

	int readline_traverse(PyObject *module, visitproc visit, void *arg);
	int readline_clear(PyObject *module);
	void readline_free(void *module);

	#define readline_module() (PyState_FindModule(&readlinemodule))
	#define readline_state(m) ((readlinestate *) PyModule_GetState(m))
	#define readlinestate_global (readline_state(readline_module()))
#else
	extern readlinestate _py2_readlinestate;

	#define readline_module() ((PyObject *) NULL)
	#define readline_state(m) (&_py2_readlinestate)
	#define readlinestate_global (&_py2_readlinestate)
	#define PyModule_GetState(m) (&_py2_readlinestate)
#endif

#endif /* __MODULESTATE_H__ */

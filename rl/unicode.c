#include "Python.h"
#include "unicode.h"


/* Unicode support */

#if (PY_MAJOR_VERSION >= 3)

/* See PEP 383 */
#define _ENCODING Py_FileSystemDefaultEncoding
#define _ERRORS "surrogateescape"


PyObject *
PyUnicode_DECODE(const char *text)
{
	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
}


PyObject *
PyUnicode_DECODE_CHAR(char character)
{
	char string[2] = "\0";

	string[0] = character;
	return PyUnicode_DECODE(string);
}


Py_ssize_t
PyUnicode_AdjustIndex(const char *text, Py_ssize_t index)
{
	PyObject *u;
	Py_ssize_t i;

	u = PyUnicode_Decode(text, index, _ENCODING, _ERRORS);
	if (u == NULL)
		return -1;
	i = PyUnicode_GET_SIZE(u);
	Py_DECREF(u);
	return i;
}


PyObject *
PyUnicode_ENCODE(PyObject *text)
{
	PyObject *u;
	PyObject *b;

	u = PyUnicode_FromObject(text);
	if (u == NULL)
		return NULL;
	b = PyUnicode_AsEncodedString(u, _ENCODING, _ERRORS);
	Py_DECREF(u);
	return b;
}


int
PyUnicode_StrConverter(PyObject *text, void *addr)
{
	PyObject *b;

	/* Cleanup stage */
	if (text == NULL) {
		Py_DECREF(*(PyObject**)addr);
		return 1;
	}
	/* Conversion stage */
	b = PyUnicode_ENCODE(text);
	if (b == NULL)
		return 0;
	if (PyBytes_GET_SIZE(b) != strlen(PyBytes_AS_STRING(b))) {
		PyErr_SetString(PyExc_TypeError, "embedded NUL character");
		Py_DECREF(b);
		return 0;
	}
	*(PyObject**)addr = b;
	return Py_CLEANUP_SUPPORTED;
}

#endif /* Python 3 */


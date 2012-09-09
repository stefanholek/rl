#include "Python.h"
#include "unicode.h"

#if (PY_MAJOR_VERSION >= 3)

/* See PEP 383 */
#define _ENCODING Py_FileSystemDefaultEncoding
#define _ERRORS "surrogateescape"


/* Unicode support */

PyObject *
PyUnicode_DECODE(const char *text)
{
	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
}


PyObject *
PyUnicode_DECODE_CHAR(char character)
{
	char text[2] = "\0";

	text[0] = character;
	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
}


Py_ssize_t
PyUnicode_INDEX(const char *text, Py_ssize_t index)
{
	PyObject *u;
	Py_ssize_t i;

	u = PyUnicode_Decode(text, index, _ENCODING, _ERRORS);
	if (u == NULL)
		return -1;
#if (PY_VERSION_HEX >= 0x03030000)
	i = PyUnicode_GET_LENGTH(u);
#else
	i = PyUnicode_GET_SIZE(u);
#endif
	Py_DECREF(u);
	return i;
}


PyObject *
PyUnicode_ENCODE(PyObject *text)
{
	return PyUnicode_AsEncodedString(text, _ENCODING, _ERRORS);
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


int
PyUnicode_FSOrNoneConverter(PyObject *text, void *addr)
{
	PyObject *b;

	/* Cleanup stage */
	if (text == NULL) {
		Py_DECREF(*(PyObject**)addr);
		return 1;
	}
	/* Conversion stage */
	if (text == Py_None) {
		*(PyObject**)addr = NULL;
		return 1;
	}
	if (PyBytes_Check(text)) {
		b = text;
		Py_INCREF(b);
	}
	else {
		b = PyUnicode_ENCODE(text);
		if (b == NULL)
			return 0;
	}
	if (PyBytes_GET_SIZE(b) != strlen(PyBytes_AS_STRING(b))) {
		PyErr_SetString(PyExc_TypeError, "embedded NUL character");
		Py_DECREF(b);
		return 0;
	}
	*(PyObject**)addr = b;
	return Py_CLEANUP_SUPPORTED;
}

#endif /* Python 3 */


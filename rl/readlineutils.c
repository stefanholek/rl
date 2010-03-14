#include "Python.h"
#include "readlineutils.h"


/* StringArray support */

char **
StringArray_New(size_t size)
{
	char **p;

	p = calloc(size+1, sizeof(char*));
	if (p == NULL)
		PyErr_NoMemory();
	return p;
}


void
StringArray_Free(char **strings)
{
	char **p;

	if (strings) {
		for (p = strings; *p; p++)
			free(*p);
		free(strings);
	}
}


size_t
StringArray_Size(char **strings)
{
	char **p;
	size_t size = 0;

	for (p = strings; *p; p++)
		size++;
	return size;
}


int
StringArray_Insert(char ***strings, size_t pos, char *string)
{
	char **new;
	char **p;
	size_t size, i;

	size = StringArray_Size(*strings);
	if (size == -1)
		return -1;

	new = StringArray_New(size+1);
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


/* PyList from StringArray */

PyObject *
PyList_FromStringArray(char **strings)
{
	PyObject *list;
	PyObject *s;
	size_t size, i;

	size = StringArray_Size(strings);
	if (size == -1)
		return NULL;

	list = PyList_New(size);
	if (list == NULL)
		return NULL;

	for (i = 0; i < size; i++) {
#if (PY_MAJOR_VERSION >= 3)
		s = PyUnicode_DECODE(strings[i]);
#else
		s = PyString_FromString(strings[i]);
#endif
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


/* StringArray from PyList */

char **
StringArray_FromPyList(PyObject *list)
{
	char **strings;
	char **p;
	char *s = NULL;
	PyObject *r;
	Py_ssize_t size, i;
	PyObject *b = NULL;

	size = PyList_Size(list);
	if (size == -1)
		return NULL;

	strings = StringArray_New(size);
	if (strings == NULL)
		return NULL;

	for (p = strings, i = 0; i < size; i++) {
		r = PyList_GetItem(list, i);
		if (r == NULL)
			goto error;
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
		if (s == NULL) {
			PyErr_NoMemory();
			goto error;
		}
		*p++ = s;
#if (PY_MAJOR_VERSION >= 3)
		Py_DECREF(b); b = NULL;
		s = NULL;
#endif
	}
	return strings;
  error:
	Py_XDECREF(b);
	StringArray_Free(strings);
	return NULL;
}


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

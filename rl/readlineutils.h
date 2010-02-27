#ifndef __READLINEUTILS_H__
#define __READLINEUTILS_H__

#include "Python.h"

/* StringArray support */
char **StringArray_new(size_t size);
void StringArray_free(char **strings);
size_t StringArray_size(char **strings);
int StringArray_insert(char ***strings, size_t pos, char *string);

PyObject *PyList_FromStringArray(char **strings);
char **StringArray_FromPyList(PyObject *list);

#if (PY_MAJOR_VERSION >= 3)
#define PyInt_FromLong PyLong_FromLong
#define PyInt_AsLong PyLong_AsLong
#define PyString_FromString PyUnicode_DECODE

/* Unicode support */
PyObject *PyUnicode_DECODE(const char *text);
PyObject *PyUnicode_DECODE_CHAR(char character);
Py_ssize_t PyUnicode_AdjustIndex(const char *text, Py_ssize_t index);
PyObject *PyUnicode_ENCODE(PyObject *text);
int PyUnicode_StrConverter(PyObject *text, void *addr);
#endif

#endif /* __READLINEUTILS_H__ */

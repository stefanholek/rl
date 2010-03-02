#ifndef __READLINEUTILS_H__
#define __READLINEUTILS_H__

#include "Python.h"

/* StringArray support */
char **StringArray_New(size_t size);
void StringArray_Free(char **strings);
size_t StringArray_Size(char **strings);
int StringArray_Insert(char ***strings, size_t pos, char *string);
PyObject *PyList_FromStringArray(char **strings);
char **StringArray_FromPyList(PyObject *list);

/* Unicode support */
#if (PY_MAJOR_VERSION >= 3)
PyObject *PyUnicode_DECODE(const char *text);
PyObject *PyUnicode_DECODE_CHAR(char character);
Py_ssize_t PyUnicode_AdjustIndex(const char *text, Py_ssize_t index);
PyObject *PyUnicode_ENCODE(PyObject *text);
int PyUnicode_StrConverter(PyObject *text, void *addr);
#endif

#endif /* __READLINEUTILS_H__ */

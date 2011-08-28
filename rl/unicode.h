#ifndef __UNICODE_H__
#define __UNICODE_H__

#include "Python.h"

#if (PY_MAJOR_VERSION >= 3)
PyObject *PyUnicode_DECODE(const char *text);
PyObject *PyUnicode_DECODE_CHAR(char character);
Py_ssize_t PyUnicode_INDEX(const char *text, Py_ssize_t index);
PyObject *PyUnicode_ENCODE(PyObject *text);
int PyUnicode_StrConverter(PyObject *text, void *addr);
int PyUnicode_FSOrNoneConverter(PyObject *text, void *addr);
#endif

#endif /* __UNICODE_H__ */

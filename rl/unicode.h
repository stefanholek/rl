#ifndef __UNICODE_H__
#define __UNICODE_H__

#include "Python.h"

#if (PY_MAJOR_VERSION >= 3)
PyObject *PyUnicode_DECODE(const char *text);
PyObject *PyUnicode_ENCODE(PyObject *text);

PyObject *PyUnicode_FS_DECODE(const char *text);
PyObject *PyUnicode_FS_ENCODE(PyObject *text);

PyObject *PyUnicode_DECODE_CHAR(char character);
Py_ssize_t PyUnicode_INDEX(const char *text, Py_ssize_t index);

int PyUnicode_StrConverter(PyObject *text, void *addr);
int PyUnicode_FSOrNoneConverter(PyObject *text, void *addr);
#endif

PyObject *PyUnicode_GetPreferredEncoding();
int PyUnicode_CopyPreferredEncoding(char *buffer, Py_ssize_t buffer_size);
void PyUnicode_PrintEncodings();

#endif /* __UNICODE_H__ */

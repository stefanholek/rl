#ifndef __STRINGARRAY_H__
#define __STRINGARRAY_H__

#include "Python.h"

char **StringArray_New(Py_ssize_t size);
void StringArray_Free(char **strings);
Py_ssize_t StringArray_Size(char **strings);
int StringArray_Insert(char ***strings, Py_ssize_t pos, char *string);
PyObject *PyList_FromStringArray(char **strings);
char **StringArray_FromPyList(PyObject *list);

#endif /* __STRINGARRAY_H__ */

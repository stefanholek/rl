#include "Python.h"
#include "unicode.h"

#if (PY_MAJOR_VERSION >= 3)

/* See PEP 383 */
#define _FS_ENCODING Py_FileSystemDefaultEncoding

#if (PY_VERSION_HEX >= 0x03060000)
#define _FS_ERRORS Py_FileSystemDefaultEncodeErrors
#else
#define _FS_ERRORS "surrogateescape"
#endif

/* Make preferred encoding available in scope */
#define USE_ENCODING \
	char _ENCODING[32]; \
	PyUnicode_CopyPreferredEncoding(_ENCODING, 32);

#define _ERRORS "surrogateescape"


/* Unicode support */

PyObject *
PyUnicode_DECODE(const char *text)
{
	USE_ENCODING

	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
}


PyObject *
PyUnicode_DECODE_CHAR(char character)
{
	char text[2] = "\0";

	USE_ENCODING

	text[0] = character;
	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
}


Py_ssize_t
PyUnicode_INDEX(const char *text, Py_ssize_t index)
{
	PyObject *u;
	Py_ssize_t i;

	USE_ENCODING

	u = PyUnicode_Decode(text, index, _ENCODING, _ERRORS);
	if (u == NULL)
		return -1;

	i = PyUnicode_GET_LENGTH(u);
	Py_DECREF(u);
	return i;
}


PyObject *
PyUnicode_ENCODE(PyObject *text)
{
	USE_ENCODING

	return PyUnicode_AsEncodedString(text, _ENCODING, _ERRORS);
}


PyObject *
PyUnicode_FS_DECODE(const char *text)
{
	return PyUnicode_Decode(text, strlen(text), _FS_ENCODING, _FS_ERRORS);
}


PyObject *
PyUnicode_FS_ENCODE(PyObject *text)
{
	return PyUnicode_AsEncodedString(text, _FS_ENCODING, _FS_ERRORS);
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
		b = PyUnicode_FS_ENCODE(text);
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


PyObject *
PyUnicode_GetPreferredEncoding()
{
	PyObject *locale = NULL;
	PyObject *getpreferredencoding = NULL;
	PyObject *r = NULL;

	locale = PyImport_ImportModule("locale");
	if (locale == NULL)
		goto error;

	getpreferredencoding = PyObject_GetAttrString(locale, "getpreferredencoding");
	if (getpreferredencoding == NULL)
		goto error;

	r = PyObject_CallFunction(getpreferredencoding, "i", 0);
	if (r == NULL)
		goto error;

	Py_DECREF(locale);
	Py_DECREF(getpreferredencoding);
	return r;
  error:
	Py_XDECREF(locale);
	Py_XDECREF(getpreferredencoding);
	return NULL;
}


int
PyUnicode_CopyPreferredEncoding(char *buffer, Py_ssize_t max_bytes)
{
	PyObject *u = NULL;
	PyObject *b = NULL;
	Py_ssize_t len;

#if (PY_MAJOR_VERSION >= 3)
	u = PyUnicode_GetPreferredEncoding();
	if (u == NULL)
		goto error;
	b = PyUnicode_AsASCIIString(u);
#else
	b = PyUnicode_GetPreferredEncoding();
#endif
	if (b == NULL)
		goto error;

	len = PyBytes_GET_SIZE(b);
	if (len >= max_bytes)
		len = max_bytes - 1;

	strncpy(buffer, PyBytes_AS_STRING(b), len);
	buffer[len] = '\0';

	Py_XDECREF(u);
	Py_DECREF(b);
	return 1;
  error:
	Py_XDECREF(u);
	Py_XDECREF(b);
	return 0;
}


void
PyUnicode_PrintEncodings()
{
	char buffer[32];
	PyUnicode_CopyPreferredEncoding(buffer, 32);
	printf("%s %s\n", buffer, Py_FileSystemDefaultEncoding);
}


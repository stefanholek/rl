#include "Python.h"
#include "unicode.h"

#if (PY_MAJOR_VERSION >= 3)

/* PyMem_RawMalloc appeared in Python 3.4 */
#if (PY_VERSION_HEX < 0x03040000)
#define PyMem_RawMalloc PyMem_Malloc
#define PyMem_RawFree PyMem_Free
#endif

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

/* Set to 1 for explicit codecs, 0 for default conversions */
#define USE_CODECS 1


/* Unicode support */

PyObject *
PyUnicode_DECODE(const char *text)
{
#if USE_CODECS
	USE_ENCODING

	return PyUnicode_Decode(text, strlen(text), _ENCODING, _ERRORS);
#else
	return PyUnicode_DecodeLocale(text, _ERRORS);
#endif
}


PyObject *
PyUnicode_DECODE_CHAR(char character)
{
	char text[2] = "\0";

	text[0] = character;
	return PyUnicode_DECODE(text);
}


Py_ssize_t
PyUnicode_INDEX(const char *text, Py_ssize_t index)
{
	PyObject *u;
	Py_ssize_t i;

#if USE_CODECS
	USE_ENCODING

	u = PyUnicode_Decode(text, index, _ENCODING, _ERRORS);
#else
	char *s;
	size_t l;

	/* Short-circuit */
	if (index == 0)
		return 0;

	/* LAME!!1!1 */
	l = strlen(text);
	if (index > l)
		index = l;
	s = PyMem_RawMalloc(index+1);
	if (s == NULL)
		return -1;
	strncpy(s, text, index);
	s[index] = '\0';
	u = PyUnicode_DecodeLocale(s, _ERRORS);
	PyMem_RawFree(s);
#endif
	if (u == NULL)
		return -1;

	i = PyUnicode_GET_LENGTH(u);
	Py_DECREF(u);
	return i;
}


PyObject *
PyUnicode_ENCODE(PyObject *text)
{
#if USE_CODECS
	USE_ENCODING

	return PyUnicode_AsEncodedString(text, _ENCODING, _ERRORS);
#else
	return PyUnicode_EncodeLocale(text, _ERRORS);
#endif
}


PyObject *
PyUnicode_FS_DECODE(const char *text)
{
#if USE_CODECS
	return PyUnicode_Decode(text, strlen(text), _FS_ENCODING, _FS_ERRORS);
#else
	return PyUnicode_DecodeFSDefault(text);
#endif
}


PyObject *
PyUnicode_FS_ENCODE(PyObject *text)
{
#if USE_CODECS
	return PyUnicode_AsEncodedString(text, _FS_ENCODING, _FS_ERRORS);
#else
	return PyUnicode_EncodeFSDefault(text);
#endif
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
#if (PY_VERSION_HEX >= 0x03060000)
	{
		PyObject *path = PyOS_FSPath(text);
		if (path == NULL)
			return 0;
		if (PyBytes_Check(path))
			b = path;
		else {
			b = PyUnicode_FS_ENCODE(path);
			Py_DECREF(path);
			if (b == NULL)
				return 0;
		}
	}
#else
	if (PyBytes_Check(text)) {
		b = text;
		Py_INCREF(b);
	}
	else {
		b = PyUnicode_FS_ENCODE(text);
		if (b == NULL)
			return 0;
	}
#endif
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


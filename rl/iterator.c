#include "Python.h"

/* GNU readline definitions */
#undef HAVE_CONFIG_H  /* Else readline/chardefs.h includes strings.h */
#define _FUNCTION_DEF /* Else readline/rltypedefs.h defines old-style types */
#ifdef __STDC__
#define PREFER_STDARG /* Use well-formed function prototypes */
#define USE_VARARGS
#endif
#include <readline/history.h>

/* Custom definitions */
#include "iterator.h"
#include "unicode.h"

/* Python 3 compatibility */
#if (PY_MAJOR_VERSION >= 3)
#define PyInt_FromLong PyLong_FromLong
#define PyInt_FromSsize_t PyLong_FromSsize_t
#define PyString_FromString PyUnicode_DECODE
#endif


/* The following borrows heavily from list iterators */

/*********************** History Iterator **************************/

typedef struct {
    PyObject_HEAD
    long it_index;
    HIST_ENTRY **it_seq; /* Set to NULL when iterator is exhausted */
} histiterobject;

static void histiter_dealloc(histiterobject *);
static int histiter_traverse(histiterobject *, visitproc, void *);
static PyObject *histiter_next(histiterobject *);
static PyObject *histiter_len(histiterobject *);

PyDoc_STRVAR(length_hint_doc, "Private method returning an estimate of len(list(it)).");

static PyMethodDef histiter_methods[] = {
    {"__length_hint__", (PyCFunction)histiter_len, METH_NOARGS, length_hint_doc},
    {NULL,              NULL}           /* sentinel */
};

PyTypeObject PyHistIter_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "historyiterator",                          /* tp_name */
    sizeof(histiterobject),                     /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)histiter_dealloc,               /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)histiter_traverse,            /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)histiter_next,                /* tp_iternext */
    histiter_methods,                           /* tp_methods */
    0,                                          /* tp_members */
};


PyObject *
HistoryIterator_New(void)
{
    histiterobject *it;

    it = PyObject_GC_New(histiterobject, &PyHistIter_Type);
    if (it == NULL)
        return NULL;
    it->it_index = 0;
    it->it_seq = history_list();
    _PyObject_GC_TRACK(it);
    return (PyObject *)it;
}

static void
histiter_dealloc(histiterobject *it)
{
    _PyObject_GC_UNTRACK(it);
    PyObject_GC_Del(it);
}

static int
histiter_traverse(histiterobject *it, visitproc visit, void *arg)
{
    Py_VISIT(it->it_seq);
    return 0;
}

static PyObject *
histiter_next(histiterobject *it)
{
    Py_ssize_t index;
    HIST_ENTRY **seq;
    PyObject *item;

    assert(it != NULL);
    if (it->it_seq == NULL)
        return NULL;
    index = it->it_index;
    seq = history_list();

    if (index < history_length) {
        item = PyString_FromString(seq[index]->line);
        if (item == NULL)
            goto error;
        ++it->it_index;
        return item;
    }
error:
    it->it_seq = NULL;
    return NULL;
}

static PyObject *
histiter_len(histiterobject *it)
{
    Py_ssize_t len;
    if (it->it_seq != NULL) {
        len = history_length - it->it_index;
        if (len >= 0)
            return PyInt_FromSsize_t(len);
    }
    return PyInt_FromLong(0);
}


/*********************** History Reverse Iterator **************************/

typedef struct {
    PyObject_HEAD
    Py_ssize_t it_index;
    HIST_ENTRY **it_seq; /* Set to NULL when iterator is exhausted */
} histreviterobject;

static void histreviter_dealloc(histreviterobject *);
static int histreviter_traverse(histreviterobject *, visitproc, void *);
static PyObject *histreviter_next(histreviterobject *);
static PyObject *histreviter_len(histreviterobject *);

static PyMethodDef histreviter_methods[] = {
    {"__length_hint__", (PyCFunction)histreviter_len, METH_NOARGS, length_hint_doc},
    {NULL,              NULL}           /* sentinel */
};

PyTypeObject PyHistRevIter_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "historyreverseiterator",                   /* tp_name */
    sizeof(histreviterobject),                  /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)histreviter_dealloc,            /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)histreviter_traverse,         /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)histreviter_next,             /* tp_iternext */
    histreviter_methods,                        /* tp_methods */
    0,
};


PyObject *
HistoryReverseIterator_New(void)
{
    histreviterobject *it;

    it = PyObject_GC_New(histreviterobject, &PyHistRevIter_Type);
    if (it == NULL)
        return NULL;
    it->it_index = history_length - 1;
    it->it_seq = history_list();
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

static void
histreviter_dealloc(histreviterobject *it)
{
    PyObject_GC_UnTrack(it);
    PyObject_GC_Del(it);
}

static int
histreviter_traverse(histreviterobject *it, visitproc visit, void *arg)
{
    Py_VISIT(it->it_seq);
    return 0;
}

static PyObject *
histreviter_next(histreviterobject *it)
{
    Py_ssize_t index;
    HIST_ENTRY **seq;
    PyObject *item;

    assert(it != NULL);
    if (it->it_seq == NULL)
        return NULL;
    index = it->it_index;
    seq = history_list();

    if (index >= 0 && index < history_length) {
        item = PyString_FromString(seq[index]->line);
        if (item == NULL)
            goto error;
        it->it_index--;
        return item;
    }
error:
    it->it_seq = NULL;
    return NULL;
}

static PyObject *
histreviter_len(histreviterobject *it)
{
    Py_ssize_t len;
    if (it->it_seq != NULL) {
        len = it->it_index + 1;
        if (len >= 0 && len <= history_length)
            return PyInt_FromSsize_t(len);
    }
    return PyInt_FromLong(0);
}


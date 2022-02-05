#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <numpy/arrayobject.h>
#include <numpy/ufuncobject.h>
#include <Python.h>


static double foo_inner(double a, double b)
{
    return a + b;
}


static void foo_loop(
    char **args,
    const npy_intp *dimensions,
    const npy_intp *steps,
    void *NPY_UNUSED(data)
) {
   const npy_intp n = dimensions[0];
   for (npy_intp i = 0; i < n; i ++)
   {
       *(double *) &args[2][i * steps[2]] = foo_inner(
       *(double *) &args[0][i * steps[0]],
       *(double *) &args[1][i * steps[1]]);
   }
}


static PyUFuncGenericFunction foo_loops[] = {foo_loop};
static char foo_types[] = {NPY_DOUBLE, NPY_DOUBLE, NPY_DOUBLE};
static void *foo_data[] = {NULL};
static const char foo_name[] = "foo";
static const char foo_docstring[] = ">>> foo(1, 2)\n3.0";

static PyModuleDef moduledef = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_module2",
    .m_size = -1
};


PyMODINIT_FUNC PyInit__module2(void)
{
    import_array();
    import_ufunc();

    PyObject *module = PyModule_Create(&moduledef);
    if (!module)
        return NULL;

    PyObject *obj = PyUFunc_FromFuncAndData(
        foo_loops, foo_data, foo_types, 1, 2, 1, PyUFunc_None, foo_name,
        foo_docstring, 0);
    if (!obj)
    {
        Py_DECREF(module);
        return NULL;
    }
    if (PyModule_AddObject(module, foo_name, obj) < 0)
    {
        Py_DECREF(obj);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}

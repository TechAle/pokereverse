#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <Python.h>
#include <sys/types.h>
#include <mach/mach_init.h>
#include <mach/mach_traps.h>
#include <mach/mach_types.h>
#include <mach/mach_vm.h>

static PyObject *MachError;

static PyObject *mach_error(kern_return_t ret) {
    return PyErr_Format(MachError, "kernel return code %d", (int)ret);
}

static PyObject *pymach_task_self(PyObject *self, PyObject *args) {
    return Py_BuildValue("i", mach_task_self());
}

static PyObject *pymach_task_for_pid(PyObject *self, PyObject *args) {
    int pid;
    task_t task;
    kern_return_t ret;
    if (!PyArg_ParseTuple(args, "i", &pid)) return NULL;
    ret = task_for_pid(mach_task_self(), pid, &task);
    if (ret) return mach_error(ret);
    return Py_BuildValue("i", task);
}

static PyObject *pymach_vm_protect(PyObject *self, PyObject *args) {
    task_t task;
    mach_vm_address_t address;
    mach_vm_size_t size;
    int prot;
    kern_return_t ret;
    if (!PyArg_ParseTuple(args, "iKLi", &task, &address, &size, &prot)) return NULL;
    ret = mach_vm_protect(task, address, size, 0, prot);
    if (ret) return mach_error(ret);
    Py_RETURN_NONE;
}

static PyObject *pymach_vm_read(PyObject *self, PyObject *args) {
    task_t task;
    mach_vm_address_t address;
    mach_vm_size_t size;
    vm_offset_t data;
    mach_msg_type_number_t dataCnt;
    kern_return_t ret;
    if (!PyArg_ParseTuple(args, "iKL", &task, &address, &size)) return NULL;
    ret = mach_vm_read(task, address, size, &data, &dataCnt);
    if (ret) return mach_error(ret);
    PyObject *val = Py_BuildValue("y#", (const char *)data, dataCnt);  // Changed "s#" to "y#"
    mach_vm_deallocate(mach_task_self(), data, dataCnt);
    return val;
}

static PyObject *pymach_vm_write(PyObject *self, PyObject *args) {
    task_t task;
    mach_vm_address_t address;
    char *buf;
    Py_ssize_t len;  // Changed from int to Py_ssize_t
    kern_return_t ret;
    if (!PyArg_ParseTuple(args, "iKy#", &task, &address, &buf, &len)) return NULL;  // Changed "t#" to "y#"
    ret = mach_vm_write(task, address, (vm_offset_t)buf, (mach_msg_type_number_t)len);
    if (ret) return mach_error(ret);
    Py_RETURN_NONE;
}

static PyMethodDef MachMethods[] = {
    {"task_self", pymach_task_self, METH_VARARGS,
     "Get a Mach port for the current task"},
    {"task_for_pid", pymach_task_for_pid, METH_VARARGS,
     "Get a Mach port for the task corresponding to a pid"},
    {"vm_protect", pymach_vm_protect, METH_VARARGS,
     "Change memory protection in another task"},
    {"vm_read", pymach_vm_read, METH_VARARGS,
     "Read memory from another task"},
    {"vm_write", pymach_vm_write, METH_VARARGS,
     "Write memory to another task"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef machmodule = {
    PyModuleDef_HEAD_INIT,
    "mach",          /* name of module */
    NULL,            /* module documentation, may be NULL */
    -1,              /* size of per-interpreter state of the module,
                        or -1 if the module keeps state in global variables. */
    MachMethods      /* module methods */
};

PyMODINIT_FUNC PyInit_mach(void) {  // Changed from initmach to PyInit_mach
    PyObject *m = PyModule_Create(&machmodule);
    if (!m) return NULL;

    MachError = PyErr_NewException("mach.MachError", NULL, NULL);
    if (MachError == NULL) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(MachError);
    if (PyModule_AddObject(m, "MachError", MachError) < 0) {
        Py_DECREF(MachError);
        Py_DECREF(m);
        return NULL;
    }

    // Changed all PyInt_FromLong to PyLong_FromLong
    PyModule_AddObject(m, "VM_PROT_NONE", PyLong_FromLong(VM_PROT_NONE));
    PyModule_AddObject(m, "VM_PROT_READ", PyLong_FromLong(VM_PROT_READ));
    PyModule_AddObject(m, "VM_PROT_WRITE", PyLong_FromLong(VM_PROT_WRITE));
    PyModule_AddObject(m, "VM_PROT_EXECUTE", PyLong_FromLong(VM_PROT_EXECUTE));
    PyModule_AddObject(m, "VM_PROT_DEFAULT", PyLong_FromLong(VM_PROT_DEFAULT));
    PyModule_AddObject(m, "VM_PROT_ALL", PyLong_FromLong(VM_PROT_ALL));

    return m;
}
cdef class Matrix :
    cdef Py_ssize_t rows
    cdef Py_ssize_t cols
    cdef double* data

    cpdef Matrix add(self, Matrix other)
    cpdef Matrix sub(self, Matrix other)
    cpdef Matrix matmul(self, Matrix other)
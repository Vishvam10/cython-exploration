# cython: language_level=3
# cython: boundscheck=False, wraparound=False, nonecheck=False

from libc.stdlib cimport malloc, free

cdef class Matrix :

    def __cinit__(self, Py_ssize_t rows, Py_ssize_t cols) :
        self.rows = rows
        self.cols = cols
        self.data = <double*> malloc(rows * cols * sizeof(double))

        if self.data == NULL :
            raise MemoryError("Matrix must have some data")
    
    def __dealloc__(self) :
        if self.data != NULL :
            free(self.data)
    
    def __str__(self):
        cdef Py_ssize_t i, j
        lines = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(str(self.data[i * self.cols + j]))
            lines.append("[ " + ", ".join(row) + " ]")
        return "\n".join(lines)

    def __repr__(self):
        return f"Matrix({self.rows}, {self.cols})\n{self.__str__()}"

    @classmethod
    def from_list(cls, list values):
        cdef Py_ssize_t r = len(values)
        if r == 0:
            raise ValueError("Empty list")
        cdef Py_ssize_t c = len(values[0])
        cdef Matrix m = cls(r, c)
        cdef Py_ssize_t i, j
        for i in range(r):
            if len(values[i]) != c:
                raise ValueError("Jagged list")
            for j in range(c):
                m.data[i * c + j] = values[i][j]
        return m


    cpdef Matrix add(self, Matrix other) :

        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Shape mismatch")
        
        cdef Matrix out = Matrix(self.rows, self.cols)
        cdef Py_ssize_t i, n = self.rows * self.cols

        for i in range(n) :
            out.data[i] = self.data[i] + other.data[i]
        
        return out

    
    cpdef Matrix sub(self, Matrix other) :

        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Shape mismatch")
        
        cdef Matrix out = Matrix(self.rows, self.cols)
        cdef Py_ssize_t i, n = self.rows * self.cols

        for i in range(n) :
            out.data[i] = self.data[i] - other.data[i]
        
        return out

        
    cpdef Matrix matmul(self, Matrix other) :

        if self.cols != other.rows:
            raise ValueError("Shape mismatch")

        cdef Matrix out = Matrix(self.rows, other.cols)
        cdef Py_ssize_t i, j, k

        for i in range(self.rows):
            for j in range(other.cols):
                out.data[i * other.cols + j] = 0.0
                for k in range(self.cols):
                    out.data[i * other.cols + j] += (
                        self.data[i * self.cols + k] *
                        other.data[k * other.cols + j]
                    )

        return out
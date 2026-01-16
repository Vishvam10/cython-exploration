class PyMatrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = [0.0] * (rows * cols)

    @classmethod
    def from_list(cls, values):
        r = len(values)
        if r == 0:
            raise ValueError("Empty list")
        c = len(values[0])

        m = cls(r, c)
        for i in range(r):
            if len(values[i]) != c:
                raise ValueError("Jagged list")
            for j in range(c):
                m.data[i * c + j] = float(values[i][j])
        return m

    def add(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Shape mismatch")

        out = PyMatrix(self.rows, self.cols)
        for i in range(self.rows * self.cols):
            out.data[i] = self.data[i] + other.data[i]
        return out

    def sub(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Shape mismatch")

        out = PyMatrix(self.rows, self.cols)
        for i in range(self.rows * self.cols):
            out.data[i] = self.data[i] - other.data[i]
        return out

    def matmul(self, other):
        if self.cols != other.rows:
            raise ValueError("Shape mismatch")

        out = PyMatrix(self.rows, other.cols)

        for i in range(self.rows):
            for j in range(other.cols):
                s = 0.0
                for k in range(self.cols):
                    s += (
                        self.data[i * self.cols + k] *
                        other.data[k * other.cols + j]
                    )
                out.data[i * other.cols + j] = s
        return out


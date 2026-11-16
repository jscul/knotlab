"""Find an actual two-axis witness by examining all outside rows in parallel."""


class PackedFaces:
    def __init__(self, tables, m):
        first, second = tables
        self.full = (1 << (1 << m)) - 1
        left, right = self.full ^ first, self.full ^ second
        self.colors = left & right, first & right, left & second, first & second
        self.low = tuple(self.full // ((1 << (1 << i)) + 1) for i in range(m))

    def first(self, i, j):
        """Least full-width outside assignment with both varying bits cleared, or None."""
        a, b = 1 << i, 1 << j
        present = []
        for color in self.colors:
            either_a = color | (color >> a)
            present.append(either_a | (either_a >> b))
        w, x, y, z = present
        at_least_three = (w & x & (y | z)) | (y & z & (w | x))
        valid = at_least_three & self.low[i] & self.low[j]
        return (valid & -valid).bit_length() - 1 if valid else None

"""Independent count extraction and fixed bin transports for result replay."""

from collections import Counter
from itertools import product


FIXED_CODING = tuple((5 * column + 3) % 16 for column in range(16))
TURN_BIN = tuple(((word & 2) << 2) | ((word & 8) >> 1) | ((word & 1) << 1) | ((word & 4) >> 2)
                 for word in range(16))


def counts(pixels):
    if len(pixels) != 64 or set(pixels) - {"0", "1"}:
        raise ValueError("Expected an ASCII 8 by 8 binary bitmap")

    def window_bin(row, col):
        index = 0
        for dr, dc in product((0, 1), repeat=2):
            r, c = row + dr, col + dc
            bit = int(pixels[8 * r + c]) if 0 <= r < 8 and 0 <= c < 8 else 0
            index = 2 * index + bit
        return index

    histogram = Counter(window_bin(row, col) for row, col in product(range(-1, 8), repeat=2))
    return tuple(histogram[pattern] for pattern in range(16))

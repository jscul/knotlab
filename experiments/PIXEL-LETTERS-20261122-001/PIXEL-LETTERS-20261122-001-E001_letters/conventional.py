"""Two conventional controls trained on each emitted guess and correctness bit."""

from fractions import Fraction


def histogram(pixels):
    """Count raw words independently of the knot apparatus, with a black border."""
    padded = [[0] * 10]
    for offset in range(0, 64, 8):
        padded.append([0, *pixels[offset:offset + 8], 0])
    padded.append([0] * 10)
    counts = [0] * 16
    for r in range(9):
        for c in range(9):
            top = 2 * padded[r][c] + padded[r][c + 1]
            bottom = 2 * padded[r + 1][c] + padded[r + 1][c + 1]
            counts[4 * top + bottom] += 1
    return counts


class IntegerMeans:
    def __init__(self, state=None):
        self.totals = state if state is not None else [[0] * 16 for _ in range(2)]

    def predict(self, pixels):
        h = histogram(pixels)
        costs = {}
        for action, row in enumerate(self.totals):
            count = sum(row) // 81
            if count:
                costs[action] = sum((x - Fraction(y, count))**2 for x, y in zip(h, row))
        return min(costs, key=costs.get) if costs else 0

    def learn(self, pixels, guessed, correct):
        row = self.totals[guessed if correct else 1 - guessed]
        for i, value in enumerate(histogram(pixels)):
            row[i] += value

    def export_memory(self):
        return self.totals


class NearestBitmap:
    def __init__(self, state=None):
        self.examples = state if state is not None else []

    def predict(self, pixels):
        if not self.examples:
            return 0
        value = int("".join(map(str, pixels)), 2)
        distances = [((value ^ int(raw, 2)).bit_count(), action) for raw, action in self.examples]
        nearest = min(distance for distance, _ in distances)
        votes = [action for distance, action in distances if distance == nearest]
        return int(2 * sum(votes) > len(votes))

    def learn(self, pixels, guessed, correct):
        self.examples.append(["".join(map(str, pixels)), guessed if correct else 1 - guessed])

    def export_memory(self):
        return self.examples


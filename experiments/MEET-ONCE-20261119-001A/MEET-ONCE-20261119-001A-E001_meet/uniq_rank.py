"""GF(2) rank, as in UNIQUE-TABLE's uniq.py (kept here so the pairing does not import the census job twice)."""


def rank(words):
    basis = {}
    for w in words:
        while w:
            top = w.bit_length() - 1
            if top in basis:
                w ^= basis[top]
            else:
                basis[top] = w
                break
    return len(basis), basis

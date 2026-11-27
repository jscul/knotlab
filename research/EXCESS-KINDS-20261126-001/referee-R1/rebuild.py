"""Exact finite checks from the seven printed rules. No project imports."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import product

BITS = (0, 1)


def nae(*bits):
    return min(bits) != max(bits)


def old_words(limit):
    rows = Counter()
    for number, word in enumerate(product(BITS, repeat=12)):
        if number >= limit:
            break
        a, b, c, d, e, f, s, t, h, i, j, k = word
        if (nae(a, b, s) and nae(a, c, t) and b ^ h ^ i == 0
                and c ^ h ^ i == 1 and e ^ j ^ k == 0
                and s ^ j ^ k == 1 and d ^ e ^ f ^ t == 1):
            rows[word[:3], word[3:6]] += 1
    return rows


def lifts(old, setting):
    return [v for v in BITS if nae(old[0], old[1 + setting], v)]


def table(rows, alice, bob, start=False):
    cells = Counter()
    for (a, b), mass in rows.items():
        al, bl = lifts(a, alice(a)), lifts(b, bob(b))
        per = Fraction(mass, len(al) * len(bl)) if start else mass
        for u, v in product(al, bl):
            cells[a + (u,), b + (v,)] += per
    return cells


def const(x):
    return lambda _: x


def marginal(cells, party):
    counts = Counter()
    for pair, mass in cells.items():
        counts[pair[party]] += mass
    return normalized(counts)


def normalized(counts):
    return {item: Fraction(n, sum(counts.values())) for item, n in counts.items()}


def tv(p, q):
    return sum(abs(p.get(k, 0) - q.get(k, 0)) for k in p.keys() | q.keys()) / 2


def old_table(cells):
    counts = Counter()
    for (a, b), mass in cells.items():
        counts[a[:3], b[:3]] += mass
    return normalized(counts)


def maximum(tables, alice_old, bob_old):
    # Given both old records, fresh choices are independent and locally uniform.
    # Any binary read using them is a mixture of deterministic old-record reads.
    # Enumerate Alice's maps. Optimize Bob's sign for each y and old record.
    cells = {xy: old_table(t) for xy, t in tables.items()}
    aa = list(product((-1, 1), repeat=len(alice_old)))
    terms = {
        (x, y, signs): [
            sum(sign * cells[x, y].get((a, b), 0)
                for sign, a in zip(signs, alice_old)) for b in bob_old
        ]
        for signs in aa for x, y in product(BITS, repeat=2)
    }
    return max(sum(abs(p + (1 if y == 0 else -1) * q)
                   for y in BITS for p, q in zip(terms[0, y, u], terms[1, y, v]))
               for u, v in product(aa, repeat=2))


def policies(rows, support, party):
    # Bit i chooses setting 1 on the i-th supported old record.
    equal, largest, first, example_equal = [], [], [], []
    for far in BITS:
        settings = [const(0), const(0)]
        settings[1 - party] = const(far)
        baseline = marginal(table(rows, *settings), 1 - party)
        distances = []
        for code in range(1 << len(support)):
            choices = {key: code >> i & 1 for i, key in enumerate(support)}
            settings[party] = choices.__getitem__
            after = marginal(table(rows, *settings), 1 - party)
            distances.append(tv(baseline, after))
            if code == 1:
                event = next((k for k in sorted(baseline.keys() | after.keys())
                              if baseline.get(k, 0) != after.get(k, 0)), None)
                if event is not None:
                    first.append((far, event, baseline.get(event, 0), after.get(event, 0)))
        equal.append(distances.count(0))
        largest.append(max(distances))
        example_equal.append(next((i for i in range(1, len(distances)-1)
                                   if distances[i] == 0), None))
    return equal, largest, first, example_equal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', type=int, default=4096)
    args = parser.parse_args()
    rows = old_words(args.prefix)
    print('old assignments examined, allowed, distinct visible pairs',
          args.prefix, sum(rows.values()), len(rows))
    if args.prefix != 4096:
        return
    visible = [sorted({pair[p] for pair in rows}) for p in BITS]
    for start in (False, True):
        fixed = {xy: table(rows, *map(const, xy), start)
                 for xy in product(BITS, repeat=2)}
        hiding = all(marginal(fixed[x, 0], 0) == marginal(fixed[x, 1], 0)
                     and marginal(fixed[0, x], 1) == marginal(fixed[1, x], 1)
                     for x in BITS)
        print('count from', 'start' if start else 'finish',
              'totals', [sum(t.values()) for t in fixed.values()],
              'both hidden', hiding, 'maximum over binary local readings',
              maximum(fixed, *visible))
        assert hiding
        assert maximum(fixed, *visible) == (2 if start else Fraction(19, 9))
    for party in BITS:
        equal, largest, first, example_equal = policies(rows, visible[party], party)
        print('sender', party, 'old records', visible[party], 'of',
              1 << len(visible[party]), 'policies equal baseline', equal,
              'largest TV from baseline', *map(str, largest))
        print('switch only first supported old record, far setting / event / before / after',
              [(far, e, str(p), str(q)) for far, e, p, q in first])
        print('first nonconstant selector identical to baseline', example_equal)


if __name__ == '__main__':
    main()

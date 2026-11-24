"""Check by the thread, 2026-11-23, for the note third_holder_moves.md.  Seven distinctions 0..6 and the seven
not-all-equal knots {i, i+1, i+3} (mod 7): the literature's Fano plane.  All seven together allow no word (recorded).
With one knot left out, the three distinctions of that knot are equal in every allowed word."""
import itertools
lines = [tuple(sorted(((i) % 7, (i + 1) % 7, (i + 3) % 7))) for i in range(7)]
def words(ls): return [w for w in itertools.product((0, 1), repeat=7) if all(not (w[a] == w[b] == w[c]) for a, b, c in ls)]
print('all seven knots: allowed words', len(words(lines)))
for out in lines:
    rest = [l for l in lines if l != out]; ws = words(rest)
    holders = [sum(1 for l in rest if d in l) for d in range(7)]
    print('without', out, ': allowed words', len(ws), '; its three distinctions equal in every word:', all(w[out[0]] == w[out[1]] == w[out[2]] for w in ws),
          '; holders of each distinction', holders)

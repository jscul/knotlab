"""All-level check of an automatic state (LEVEL-RETURN-20261113-001B): a Moore automaton M reads an address from its first letter
and its output bit is the address's value. For a description (automaton, placements) and a level class (n = p mod 2, n >= n0),
M's values are a state of the level-n pattern at every such n exactly when no reachable configuration of the product below
violates a knot. The product reads x letter by letter and tracks, for each of the placement's three words, the run of its maps and
M's run on its output, which pairs of outputs have differed so far, the length's parity and min(length, n0). A knot exists at the
end exactly when every pair has differed (three distinct images), so finite reachability decides the statement for all n."""
import itertools
from collections import deque


def step_word(aut, word_state, b):
    """word_state: current maps of the word, listed left to right (applied right to left). Returns (output letter, new state)."""
    sw, d0, d1 = aut
    c = b; new = list(word_state)
    for i in range(len(word_state) - 1, -1, -1):
        q = word_state[i]
        out = c ^ sw[q]
        new[i] = d0[q] if c == 0 else d1[q]
        c = out
    return c, tuple(new)


def check(aut, words, placements, M, p, n0, max_states=10_000_000):
    """M = (delta, out, start): delta[m][letter] -> m'. Returns (True, n_configs) or (False, counterexample)."""
    delta, out, start = M
    for pl in placements:
        ws = [tuple(words[i]) for i in pl]
        init = (tuple(ws), (start,) * 3, (False,) * 3, 0, 0, ())
        seen = {init[:5]}; dq = deque([init])
        while dq:
            runs, ms, div, par, ln, path = dq.popleft()
            for b in (0, 1):
                outs, nr = zip(*(step_word(aut, r, b) for r in runs))
                nm = tuple(delta[m][c] for m, c in zip(ms, outs))
                nd = (div[0] or outs[0] != outs[1], div[1] or outs[0] != outs[2], div[2] or outs[1] != outs[2])
                npar = (par + 1) % 2; nln = min(ln + 1, n0)
                if nln >= n0 and npar == p % 2 and all(nd):
                    v = [out[m] for m in nm]
                    if v[0] == v[1] == v[2]:
                        return False, dict(placement=pl, address=''.join(map(str, path + (b,))), values=v)
                key = (nr, nm, nd, npar, nln)
                if key not in seen:
                    seen.add(key); dq.append((nr, nm, nd, npar, nln, path + (b,) if len(path) < 64 else path))
                    if len(seen) > max_states: raise RuntimeError('too many configurations')
    return True, len(seen)


def words_of(s):
    return [()] + [(q,) for q in range(s)] + [(q, t) for q in range(s) for t in range(s)]


PARITY = ([[0, 1], [1, 0]], [0, 1], 0)                     # the word's parity
# first letter XOR last letter: states 0 start, then 1 + 2*first + last
FIRST_LAST = ([[1, 4], [1, 2], [1, 2], [3, 4], [3, 4]], [0, 0, 1, 1, 0], 0)

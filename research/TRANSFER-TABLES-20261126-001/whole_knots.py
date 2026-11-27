"""whole_knots.py: are the readers of tables.py joined by a knot in the whole? (README.md; frozen in
preregistration.md.) On the transfer law's 13 reached states (pair lift, one founder, one round): every set of two or
three distinctions whose projection of the reached states is constrained (K1), with every proper part free (K2), and
nonempty (K3), the canonical test on the reached support, here by direct projection, and one of them confirmed with the
repository's checker (knotlab check). Then: for each of tables.py's 30 splits, is some such knot (or a listed law) held
by both readers?"""
import sys, json, itertools, subprocess, os
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tables as T            # noqa: E402


def projection(words, S):
    return {tuple(int(d in w) for d in S) for w in words}


def knots_in_whole(words, n):
    out = []
    for k in (2, 3):
        for S in itertools.combinations(range(n), k):
            P = projection(words, S)
            if len(P) == 2 ** k: continue                                            # K1 fails
            if any(len(projection(words, Q)) < 2 ** (k - 1) for Q in itertools.combinations(S, k - 1)): continue   # K2
            out.append((S, sorted(P)))
    return out


def knotlab_check(S, allowed):
    names = ['v%d' % d for d in S]
    forbidden = sorted(set(itertools.product((0, 1), repeat=len(S))) - set(allowed))
    cnf = ';'.join(' '.join(('~' if b else '') + nm for b, nm in zip(word, names)) for word in forbidden)
    verdicts = []
    for contact in names:
        r = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--contact', contact,
                            '--loops', *[x for x in names if x != contact], '--json'], cwd=ROOT,
                           env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')}, capture_output=True, text=True, check=True)
        verdicts.append(json.loads(r.stdout)['is_knot'])
    return verdicts


if __name__ == '__main__':
    weights, scopes = T.reached('exact_two')
    words = list(weights); n = 9
    K = knots_in_whole(words, n)
    listed = [tuple(s) for s in scopes]
    print(json.dumps({'knots in the whole (two or three places)': [list(S) for S, _ in K],
                      'listed laws among them': [list(S) for S, _ in K if S in listed]}))
    extra = [(S, P) for S, P in K if S not in listed]
    if extra:
        S, P = extra[0]
        print(json.dumps({'checker on %s' % list(S): knotlab_check(S, P), 'allowed patterns': P}))
    joined = 0; rows = []
    for A, B, C in T.splits(n, scopes):
        j = [list(S) for S, _ in K if set(S) & set(A) and set(S) & set(B)]
        joined += bool(j); rows.append({'A': A, 'B': B, 'unread': C, 'joined by': j[:3]})
    print(json.dumps({'splits': len(rows), 'joined by a knot in the whole': joined}))
    for r in rows: print(json.dumps(r))

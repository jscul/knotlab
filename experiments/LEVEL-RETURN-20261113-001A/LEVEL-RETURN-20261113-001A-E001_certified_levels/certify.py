"""Certified verdicts for LEVEL-RETURN-20261113-001A: build the level-n pattern of a description, solve it with CaDiCaL 2.1.2 (the
Lean toolchain's binary) writing an LRAT proof, then certify: a model is checked against every knot; a refutation is checked by
lrat_check (the thread's own C checker, RUP steps only). The proof file is deleted after checking; its size and sha256 are kept."""
import hashlib, os, subprocess, sys, tempfile, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CADICAL = os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.35.0/bin/cadical')
CHECKER = os.path.join(HERE, 'lrat_check')


def act(aut, word, n):
    """Apply a word of state maps (rightmost first) to every binary address of length n (first letter most significant)."""
    sw, d0, d1 = (np.array(v) for v in aut)
    y = np.arange(1 << n, dtype=np.int64)
    for q in reversed(word):
        st = np.full(y.shape, q); out = np.zeros_like(y)
        for i in range(n - 1, -1, -1):
            b = (y >> i) & 1
            out = (out << 1) | (b ^ sw[st]); st = np.where(b == 0, d0[st], d1[st])
        y = out
    return y


def pattern(key, n):
    s, sw, d0, d1, pls = key
    W = [()] + [(q,) for q in range(s)] + [(q, t) for q in range(s) for t in range(s)]
    ks = []
    for pl in pls:
        T = np.stack([act((sw, d0, d1), W[i], n) for i in pl], 1)
        ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
        ks.append(np.sort(T[ok], 1))
    return np.unique(np.concatenate(ks), axis=0) if ks else np.zeros((0, 3), dtype=np.int64)


def certify(K, nvars, workdir, timeout):
    """K: knots (rows of three distinct variable indices, 0-based). Returns a dict with verdict alive/dead/undecided and evidence."""
    t0 = time.time()
    if len(K) == 0:
        return dict(verdict='alive', certificate='empty pattern', seconds=0.0)
    cnf = os.path.join(workdir, 'f.cnf'); prf = os.path.join(workdir, 'p.lrat')
    m = int(K.min())
    with open(cnf, 'w') as f:
        f.write(f'p cnf {nvars} {2 * len(K) + 1}\n')
        for a, b, c in K.tolist():
            f.write(f'{a+1} {b+1} {c+1} 0\n{-a-1} {-b-1} {-c-1} 0\n')
        f.write(f'{m+1} 0\n')  # complement symmetry: every state's complement is a state
    try:
        r = subprocess.run([CADICAL, '--lrat=true', '--binary=false', '-q', cnf, prf], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return dict(verdict='undecided', certificate='solver timeout', seconds=time.time() - t0)
    out = dict(seconds=None, solver_exit=r.returncode)
    if r.returncode == 10:
        lits = [int(t) for line in r.stdout.splitlines() if line.startswith('v') for t in line[1:].split()]
        val = np.zeros(nvars + 1, dtype=np.int8)
        for l in lits:
            if l != 0 and abs(l) <= nvars: val[abs(l)] = 1 if l > 0 else 0
        V = val[K + 1]
        ok = bool(np.all(V.min(1) != V.max(1))) and val[m + 1] == 1
        out.update(verdict='alive' if ok else 'checker-rejected-model', certificate='model checked against every knot')
    elif r.returncode == 20:
        size = os.path.getsize(prf); h = hashlib.sha256()
        with open(prf, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
        try:
            c = subprocess.run([CHECKER, cnf, prf], capture_output=True, text=True, timeout=timeout)
            ok = c.returncode == 0 and c.stdout.startswith('VERIFIED')
            msg = c.stdout.strip()
        except subprocess.TimeoutExpired:
            ok, msg = False, 'checker timeout'
        out.update(verdict='dead' if ok else 'unverified-refutation', certificate=f'LRAT {size} bytes sha256 {h.hexdigest()}: {msg}')
    else:
        out.update(verdict='undecided', certificate=f'solver exit {r.returncode}')
    for p in (cnf, prf):
        if os.path.exists(p): os.remove(p)
    out['seconds'] = time.time() - t0
    return out

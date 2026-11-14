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


def stream_solve(cnf, workdir, timeout):
    """Solve twice when needed: first without a proof (a model is checked by the caller); if the formula is refuted, solve again
    writing the LRAT proof to a file in the case's own work directory on disk, check it with lrat_check, and delete it. (A first
    version streamed the proof through a pipe; the checker's pace then throttled the solver.) Returns (exit code, stdout, checker
    output) or None on timeout."""
    t0 = time.time()
    try:
        r = subprocess.run([CADICAL, '-q', cnf], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 20:
        return r.returncode, r.stdout, ''
    prf = os.path.join(workdir, 'p.lrat')
    left = max(1.0, timeout - (time.time() - t0))
    try:
        r2 = subprocess.run([CADICAL, '--lrat=true', '--binary=false', '-q', cnf, prf], capture_output=True, text=True, timeout=left)
        if r2.returncode != 20:
            return r2.returncode, r2.stdout, 'second solve disagreed'
        size = os.path.getsize(prf)
        c = subprocess.run([CHECKER, cnf, prf], capture_output=True, text=True, timeout=max(1.0, timeout - (time.time() - t0)))
        return 20, r2.stdout, f'{c.stdout.strip()} ({size} bytes)'
    except subprocess.TimeoutExpired:
        return None
    finally:
        if os.path.exists(prf): os.remove(prf)

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
    res = stream_solve(cnf, workdir, timeout)
    if res is None:
        return dict(verdict='undecided', certificate='solver timeout', seconds=time.time() - t0)
    rc, stdout, chk = res
    out = dict(seconds=None, solver_exit=rc)
    if rc == 10:
        lits = [int(t) for line in stdout.splitlines() if line.startswith('v') for t in line[1:].split()]
        val = np.zeros(nvars + 1, dtype=np.int8)
        for l in lits:
            if l != 0 and abs(l) <= nvars: val[abs(l)] = 1 if l > 0 else 0
        V = val[K + 1]
        ok = bool(np.all(V.min(1) != V.max(1))) and val[m + 1] == 1
        out.update(verdict='alive' if ok else 'checker-rejected-model', certificate='model checked against every knot')
    elif rc == 20:
        ok = chk.startswith('VERIFIED')
        out.update(verdict='dead' if ok else 'unverified-refutation', certificate=f'LRAT checked: {chk}')
    else:
        out.update(verdict='undecided', certificate=f'solver exit {rc}')
    for p in (cnf, prf):
        if os.path.exists(p): os.remove(p)
    out['seconds'] = time.time() - t0
    return out


def certify_rigid(K, nvars, workdir, timeout):
    """Rigidity: find a state s (checked); then ask for a state that keeps s's value at the smallest address and differs from s
    somewhere among the addresses in knots. A checked LRAT refutation of that means s and its complement are the only states."""
    t0 = time.time()
    first = certify(K, nvars, workdir, timeout)
    if first['verdict'] != 'alive':
        return dict(verdict='not alive: ' + first['verdict'], seconds=time.time() - t0)
    cnf = os.path.join(workdir, 'f.cnf'); prf = os.path.join(workdir, 'p.lrat')
    # re-solve to get the model values (certify does not return them): small extra cost
    m = int(K.min()); used = sorted(set(K.ravel().tolist()))
    def write(extra):
        with open(cnf, 'w') as f:
            f.write(f'p cnf {nvars} {2 * len(K) + 1 + len(extra)}\n')
            for a, b, c in K.tolist(): f.write(f'{a+1} {b+1} {c+1} 0\n{-a-1} {-b-1} {-c-1} 0\n')
            f.write(f'{m+1} 0\n')
            for cl in extra: f.write(' '.join(map(str, cl)) + ' 0\n')
    write([])
    r = subprocess.run([CADICAL, '-q', cnf], capture_output=True, text=True, timeout=timeout)
    lits = [int(t) for line in r.stdout.splitlines() if line.startswith('v') for t in line[1:].split()]
    val = {abs(l): (l > 0) for l in lits if l != 0}
    diff = [(-u - 1) if val.get(u + 1, False) else (u + 1) for u in used]
    write([diff])
    res = stream_solve(cnf, workdir, timeout)
    if res is None:
        return dict(verdict='undecided', certificate='solver timeout (second state)', seconds=time.time() - t0)
    rc, stdout, chk = res
    if rc == 10:
        lits2 = [int(t) for line in stdout.splitlines() if line.startswith('v') for t in line[1:].split()]
        v2 = np.zeros(nvars + 1, dtype=np.int8)
        for l in lits2:
            if l != 0 and abs(l) <= nvars: v2[abs(l)] = 1 if l > 0 else 0
        V = v2[K + 1]; ok = bool(np.all(V.min(1) != V.max(1))) and any(bool(v2[u + 1]) != val.get(u + 1, False) for u in used)
        out = dict(verdict='not rigid' if ok else 'checker-rejected-model', certificate='second state checked')
    elif rc == 20:
        out = dict(verdict='rigid' if chk.startswith('VERIFIED') else 'unverified-refutation', certificate=f'LRAT checked: {chk}')
    else:
        out = dict(verdict='undecided', certificate=f'solver exit {rc}')
    for p in (cnf, prf):
        if os.path.exists(p): os.remove(p)
    out['seconds'] = time.time() - t0
    return out

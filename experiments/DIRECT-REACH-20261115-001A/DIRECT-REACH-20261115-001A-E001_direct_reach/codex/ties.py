"""Complete signed tie classes from checked states and certified candidate pairs."""
import collections
import random
import time
from pysat.solvers import Cadical195
from reuse import pattern, certificates as cert
from retention import ProofStore


class SignedUnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.sign = [0] * n

    def find(self, v):
        if self.parent[v] == v:
            return v, 0
        root, bit = self.find(self.parent[v])
        self.sign[v] ^= bit
        self.parent[v] = root
        return root, self.sign[v]

    def union(self, u, v, parity):
        a, x = self.find(u)
        b, y = self.find(v)
        if a == b:
            assert x ^ y == parity
        else:
            # Always attach to the smaller representative for deterministic records.
            if a > b:
                a, b = b, a
            self.parent[b] = a
            self.sign[b] = x ^ y ^ parity


def compute_ties(K, nvars, workdir, seed, samples=64, store=None):
    if samples < 64:
        raise ValueError('at least 64 random-phase states required')
    started = time.monotonic()
    store = store or ProofStore(workdir, nvars)
    cnf = pattern.clauses(K)
    rng = random.Random(seed)
    columns = [0] * nvars
    states = []

    def remember(state):
        assert cert.check_state(K, state)
        i = len(states)
        for v, bit in enumerate(state):
            columns[v] |= bit << i
        states.append(cert.pack_state(state))
        return i

    # Fresh solvers avoid CaDiCaL retaining a previous satisfied trail and
    # ignoring the new preferred phases. Disable preprocessing and lucky/walk
    # phases so the independent random per-variable phases actually take effect.
    for _ in range(samples):
        phases = [v + 1 if rng.getrandbits(1) else -v - 1 for v in range(nvars)]
        with Cadical195(bootstrap_with=cnf) as solver:
            solver.configure({'lucky': 0, 'walk': 0, 'elim': 0, 'probe': 0,
                              'subsume': 0, 'inprocessing': 0, 'forcephase': 1})
            solver.set_phases(phases)
            if not solver.solve():
                proof = store.refute(cnf, nvars, purpose='tie sampling found dead union')
                return {'verdict': 'undefined_dead_union', 'refutation': proof,
                        'classes': [], 'seconds': time.monotonic() - started}
            model = {abs(l): int(l > 0) for l in solver.get_model() or []}
            remember([model.get(v + 1, int(phases[v] > 0)) for v in range(nvars)])

    sample_seconds = time.monotonic() - started
    uf = SignedUnionFind(nvars)
    confirmations, rejected = [], []
    sat_calls = samples
    with Cadical195(bootstrap_with=cnf) as solver:
        while True:
            mask = (1 << len(states)) - 1
            groups = collections.defaultdict(list)
            for v, column in enumerate(columns):
                groups[min(column, column ^ mask)].append(v)
            candidate = None
            for group in groups.values():
                u = group[0]
                ru, _ = uf.find(u)
                for v in group[1:]:
                    if uf.find(v)[0] != ru:
                        candidate = u, v
                        break
                if candidate:
                    break
            if candidate is None:
                break
            u, v = candidate
            parity = int(columns[u] != columns[v])
            # Two calls, for exactly the two assignments violating this tie.
            refutations, counterstates = [], []
            for x in (0, 1):
                y = x ^ parity ^ 1
                units = [u + 1 if x else -u - 1, v + 1 if y else -v - 1]
                sat_calls += 1
                answer = solver.solve(assumptions=units)
                if answer:
                    state = cert.model_from_literals(solver.get_model() or [], nvars)
                    assert cert.check_state(K, state, units)
                    counterstates.append(remember(state))
                else:
                    proof = store.refute(cnf, nvars, units, purpose='tie candidate forbidden pair')
                    refutations.append(proof['cnf_sha256'])
            if len(refutations) == 2:
                uf.union(u, v, parity)
                confirmations.append({'u': u, 'v': v, 'parity': parity,
                                      'refutations': refutations})
                if len(confirmations) % 128 == 0:
                    print(f'TIES {str(seed)[:12]} confirmed={len(confirmations)} seconds={time.monotonic()-started:.1f}', flush=True)
            else:
                # Complement invariance rules out a one-sided forbidden pair.
                assert not refutations
                rejected.append({'u': u, 'v': v, 'proposed_parity': parity,
                                 'counterstate_indices': counterstates})

    classes = collections.defaultdict(list)
    signs = collections.defaultdict(list)
    for v in range(nvars):
        root, bit = uf.find(v)
        classes[root].append(v)
        signs[root].append(bit)
    nontrivial = [vs for vs in classes.values() if len(vs) > 1]
    relative_signs = [signs[vs[0]] for vs in nontrivial]
    summaries = []
    for top in (2, 3):
        for s in range(1, 7):
            spanning = [i for i, vs in enumerate(nontrivial)
                        if top in {pattern.level(v) for v in vs}
                        and top + s in {pattern.level(v) for v in vs}]
            summaries.append({'k0': top, 's': s, 'spanning': bool(spanning),
                              'class_indices': spanning})
    return {'verdict': 'complete', 'nvars': nvars, 'classes': nontrivial,
            'class_signs': relative_signs,
            'singletons': [vs[0] for vs in classes.values() if len(vs) == 1],
            'forced_pair_count': sum(len(vs)*(len(vs)-1)//2 for vs in nontrivial),
            'confirmed_candidates': confirmations, 'rejected_candidates': rejected,
            'summaries': summaries, 'state_pool': states,
            'sampling': {'solver': 'PySAT CaDiCaL 1.9.5', 'seed': str(seed),
                         'random_phase_states': samples, 'fresh_solver_per_state': True,
                         'seconds': sample_seconds, 'uniform_state_sampling_claimed': False},
            'sat_calls': sat_calls,
            'completeness': 'Every final equal/complement sample-signature class equals a certified signed-UF class; different signatures have checked counterstates. All pair relations follow from the retained two-refutation forest.',
            'seconds': time.monotonic() - started}

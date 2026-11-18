"""Gate checks for FRESH-COUNT-20261118-001B-E001.  Run from anywhere: python3 -B checks.py"""
import itertools
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import freelib as F  # noqa: E402
import ideals  # noqa: E402
import bonds  # noqa: E402

results = {}


def gate(name, ok, detail=''):
    results[name] = {'pass': bool(ok), 'detail': detail}
    print(('PASS ' if ok else 'FAIL ') + name + (f'  {detail}' if detail else ''))


# G1: the literal policy reproduces the earlier study's rounds and its referee's two- and four-bit variants
P, o, _ = F.run(3, F.uniform(3), 8, cap=3)
gate('G1a N^3 layers under the original policy', P.counts_by_round() == [comb(t + 2, 2) for t in range(9)], str(P.counts_by_round()))
P, o, _ = F.run(2, F.uniform(2), 10, cap=3)
gate('G1b two fresh bits from a two-bit seed: N^2', P.counts_by_round() == [t + 1 for t in range(11)], str(P.counts_by_round()))
P, o, _ = F.run(4, F.uniform(4), 8, cap=3)
gate('G1c four fresh bits, groups of at most three: stall at round 4', o == 'stall' and P.rounds == 3, f'{o} after {P.rounds}')

# G2: the structural implied-parity test agrees with elimination over GF(2)
mism, tested = 0, 0
for a in (3, 4):
    for rule in (F.fewest, F.axis, F.balance, F.surplus(0.3)):
        for s in range(6):
            P, o, _ = F.run(a, rule, 6, seed=s, linalg=True, max_junctions=400)
            mism += P.implied_mismatch
            tested += len(P.bits_of)
gate('G2 implied parity: structure = GF(2)', mism == 0, f'{tested} junctions, {mism} mismatches')

# G3: the ideal checker passes a grown run and fails two mutants
P, o, _ = F.run(3, F.uniform(3), 4)
ok = ideals.check(P)
good = not ok['errors'] and ok['missing'] == 0
# mutant 1: forget one junction of round 2 (its bits become loose ends of nothing): rebuild owner and neighbours without it
import copy  # noqa: E402
M = copy.deepcopy(P)
victim = next(j for j in range(len(M.bits_of)) if M.round_of[j] == 2)
for b in M.bits_of[victim]:
    M.owner[b] = [x for x in M.owner[b] if x != victim]
M.bits_of[victim] = []
M.round_of[victim] = -1
r1 = ideals.check(M)
# mutant 2: give a round-3 junction an extra parent from round 1
M2 = copy.deepcopy(P)
u = next(j for j in range(len(M2.bits_of)) if M2.round_of[j] == 1)
v = next(j for j in range(len(M2.bits_of)) if M2.round_of[j] == 3 and u not in M2.nbr[j])
nb = M2.nbits
M2.nbits += 1
M2.bits_of[u].append(nb)
M2.bits_of[v].append(nb)
M2.owner[nb] = [u, v]
r2 = ideals.check(M2)
gate('G3 ideal checker: passes N^3 to round 4, flags both mutants', good and (r1['errors'] or r1['missing']) and (r2['errors'] or r2['missing']),
     f'grown {ok}; mutant1 {r1["errors"][:1]} missing {r1["missing"]}; mutant2 {r2["errors"][:1]} missing {r2["missing"]}')


# G4: bond distances by cut enumeration = bond distances from the allowed states (K1-K3 projections), on small presentations
def states(stars, nb):
    out = []
    for x in range(1 << nb):
        if all(sum((x >> b) & 1 for b in S) % 2 == 0 for S in stars):
            out.append(x)
    return out


def proj_full(st, S):
    vals = {tuple((x >> b) & 1 for b in S) for x in st}
    return len(vals) == 1 << len(S)


def brute_dist(stars, nb):
    st = states(stars, nb)
    d = {}
    for size in range(3, nb + 1):
        for S in itertools.combinations(range(nb), size):
            if proj_full(st, S):
                continue
            if all(proj_full(st, T) for T in itertools.combinations(S, size - 1)):
                for e, f in itertools.combinations(S, 2):
                    d.setdefault((e, f), size - 1)
    return d


small = []
for a, rule, T in ((3, F.fewest, 1), (3, F.fewest, 2), (3, F.fewest, 3), (3, F.uniform(3), 1), (4, F.fewest, 1)):
    P = F.Presentation(a)
    for _ in range(T):
        P.step(rule)
    small.append(P)
agree = True
detail = []
for P in small:
    stars = [frozenset(S) for S in P.bits_of]
    _, d1 = bonds.distances(stars)
    d2 = brute_dist(stars, P.nbits)
    agree &= d1 == d2
    detail.append(f'{len(stars)}j/{P.nbits}b:{d1 == d2}')
gate('G4 bond distances: cuts = allowed states', agree, ' '.join(detail))

# G5: the reader recovers the junctions of N^3's first rounds (the earlier study's result)
ok5 = True
for T in range(3):
    P = F.Presentation(3)
    for _ in range(T):
        P.step(F.uniform(3))
    stars = [frozenset(S) for S in P.bits_of]
    allbits, d = bonds.distances(stars)
    ok5 &= set(bonds.read_stars(allbits, d, max(map(len, stars)))) == set(stars)
gate('G5 threshold reader on N^3 rounds 0-2', ok5)


# G6: forced-bit detector (bridges) = GF(2) single-bit test, on a planted forced bit and on grown runs
def gf2_forced(P):
    basis = {}
    for S in P.bits_of:
        x = 0
        for b in S:
            x |= 1 << b
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    out = []
    for b in range(P.nbits):
        x = 1 << b
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                break
        if x == 0:
            out.append(b)
    return out


def planted(P, info, rng):
    return [1 if i['implied'] else i['d'] for i in info]      # one fresh bit at the implied top: forced to 0


P, o, _ = F.run(3, planted, 3)      # rounds 1-3: the 2^3 pattern with one fresh bit on its top
plant_ok = P.forced_bits() == gf2_forced(P) and len(P.forced_bits()) == 1
same = True
for a in (3, 4):
    for rule in (F.fewest, F.axis, F.blind(3), F.surplus(0.3), F.uniform(a - 1)):
        for s in range(5):
            Q, o, _ = F.run(a, rule, 5, seed=s, max_junctions=300)
            same &= Q.forced_bits() == gf2_forced(Q)
gate('G6 forced bits: bridges = GF(2), planted bit found', plant_ok and same, f'planted {P.forced_bits()}')

# G7: the lookahead demand equals the groups actually formed next round (fewest never stalls; demand = groups used)
ok7 = True
for a in (3, 4):
    for s in range(10):
        P, o, _ = F.run(a, F.surplus(0.3), 6, seed=s, max_junctions=600)
        for j in range(len(P.bits_of)):
            if P.demand_at_birth[j] is None or P.round_of[j] == P.rounds:
                continue
            kids = [x for b in P.bits_of[j] for x in P.owner[b] if x != j and P.round_of[x] == P.round_of[j] + 1]
            multi = sum(1 for x in kids if P.parents[x] >= 2)
            ok7 &= multi == P.demand_at_birth[j]
gate('G7 demand at birth = multi-parent children formed', ok7)

json.dump(results, open(HERE / 'checks_output.json', 'w'), indent=1)
print(f'{sum(r["pass"] for r in results.values())} of {len(results)} gates pass')

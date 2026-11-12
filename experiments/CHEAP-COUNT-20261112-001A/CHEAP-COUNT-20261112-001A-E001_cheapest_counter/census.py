"""CHEAP-COUNT-20261112-001A: the cheapest NAE counter, with fresh (helper) distinctions.

S1  Exact synthesis: for f = 0..6 fresh distinctions, the fewest NAE knots on 4 named distinctions and f fresh ones whose projection
    onto the named four is exactly their even parity (SAT: a selector per knot; every odd named state fails for every fresh
    assignment; every even one has a fresh assignment; a cardinality bound, raised until satisfiable). Knots on three named
    distinctions are excluded (they forbid 0000). At the least f, all minimal gadgets are enumerated (blocking clauses, cap 20,000 or ten minutes).
S2  The counter: generations of length 3 + r (the literature's rows); each new position i's main distinction is tied to its old
    neighbours by a 4-place even parity (rule 60: new i, old i-1, old i, R; rule 90: new i, old i-1, old i+1, R; rule 150: new i,
    old i-1, old i, old i+1; hop: new i, old floor(i/2), old i, R), where a missing old position is the reference R; the last
    generation's main distinctions are closed by NAE on consecutive triples. Built twice: with the parity as its exact clauses, and
    with a minimal gadget per position on fresh distinctions (a collision of named distinctions is broken by a fresh copy tied equal
    through the inequality gadget). alive(t) for t = 1..64.
S3  Fragility: every single-knot deletion or replacement of the gadget; its projection onto the named four; the rule-60 growth with
    that relation (exact clauses), alive(t) to 64, classified (constant; period <= 16 from depth <= 32; else unexplained).
Run from the repository root:  census.py --s1  |  census.py --s2  |  census.py --s3 WORKER WORKERS  |  census.py --summary
"""
import glob, itertools, json, math, os, sys, time
from collections import Counter
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("CC_OUT") or os.path.join(HERE, "../../../artifacts/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter")
TMAX = 64


def nae_ok(vals):
    return 0 < sum(vals) < 3


def synth(f, m, extra_block=()):
    """A set of at most m knots on 4 named + f fresh distinctions projecting exactly onto even parity, or None."""
    n = 4 + f
    knots = [k for k in itertools.combinations(range(n), 3) if not all(v < 4 for v in k)]
    sel = {k: j + 1 for j, k in enumerate(knots)}
    top = len(knots)
    cl = []
    fresh_states = list(itertools.product((0, 1), repeat=f))
    for named in itertools.product((0, 1), repeat=4):
        if sum(named) % 2:
            for fr in fresh_states:
                full = named + fr
                cl.append([sel[k] for k in knots if not nae_ok([full[v] for v in k])])
        else:
            fv = list(range(top + 1, top + 1 + f)); top += f
            for k in knots:                       # chosen -> NAE holds with named fixed and fresh variables fv
                lits_or, lits_nand, const_true = [], [], False
                vals = []
                for v in k:
                    vals.append(("c", named[v]) if v < 4 else ("v", fv[v - 4]))
                # (a or b or c): a constant 1 satisfies it; (not a or not b or not c): a constant 0 satisfies it
                if not any(x == ("c", 1) for x in vals):
                    cl.append([-sel[k]] + [x[1] for x in vals if x[0] == "v"])
                if not any(x == ("c", 0) for x in vals):
                    cl.append([-sel[k]] + [-x[1] for x in vals if x[0] == "v"])
    for b in extra_block:
        cl.append([-sel[k] for k in b])
    enc = CardEnc.atmost(lits=list(sel.values()), bound=m, top_id=top, encoding=EncType.seqcounter)
    with Solver(name="cadical153", bootstrap_with=cl + enc.clauses) as s:
        if not s.solve():
            return None
        model = set(l for l in s.get_model() if l > 0)
        return [k for k in knots if sel[k] in model]


def projection(n_named, f, knots):
    rel = set()
    for full in itertools.product((0, 1), repeat=n_named + f):
        if all(nae_ok([full[v] for v in k]) for k in knots):
            rel.add(full[:n_named])
    return rel


def s1():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for f in range(0, 7):
        best = None
        for m in range(1, 25):
            g = synth(f, m)
            if g is not None:
                best = (m, g)
                break
        res[f] = dict(m=best[0] if best else None, gadget=best[1] if best else None,
                      check=sorted(projection(4, f, best[1])) == sorted(t for t in itertools.product((0, 1), repeat=4) if sum(t) % 2 == 0) if best else None)
        print(f, res[f]["m"], res[f]["check"], flush=True)
    fmin = min(f for f in res if res[f]["m"] is not None)
    m = res[fmin]["m"]
    found, block = [], []
    t0 = time.time()
    while len(found) < 20000 and time.time() - t0 < 600:
        g = synth(fmin, m, extra_block=block)
        if g is None:
            break
        found.append(g); block.append(g)
    json.dump(dict(table=res, least_f=fmin, least_m=m, minimal_gadgets_at_least_f=len(found), enumeration_complete=g is None,
                   gadgets=found[:50]), open(os.path.join(OUT, "s1.json"), "w"), indent=1)


def growth(t, parity_slots, gadget=None, rel=None):
    """Clauses of the depth-t growth. parity_slots names the four of: n0, o-1, o0, o+1, oh (old floor(i/2)), r."""
    rows, nv = [], 0
    for r in range(t + 1):
        rows.append(list(range(nv, nv + 3 + r))); nv += 3 + r
    R = nv; nv += 1
    cl = []

    def fresh():
        nonlocal nv
        nv += 1
        return nv - 1

    def nae(a, b, c):
        cl.extend([[a + 1, b + 1, c + 1], [-(a + 1), -(b + 1), -(c + 1)]])

    def neq(x, y):
        a, b, c = fresh(), fresh(), fresh()
        nae(x, y, a); nae(x, y, b); nae(x, y, c); nae(a, b, c)

    def eq(x, y):
        m = fresh(); neq(x, m); neq(m, y)

    for r in range(1, t + 1):
        old, new = rows[r - 1], rows[r]
        for i in range(len(new)):
            def slot(s):
                if s == "n0":
                    return new[i]
                if s == "r":
                    return R
                p = i // 2 if s == "oh" else i + {"o-1": -1, "o0": 0, "o+1": 1}[s]
                return old[p] if 0 <= p < len(old) else R
            vs = [slot(s) for s in parity_slots]
            if rel is not None or gadget is None:
                allowed = rel if rel is not None else {x for x in itertools.product((0, 1), repeat=4) if sum(x) % 2 == 0}
                for x in itertools.product((0, 1), repeat=4):          # forbid each state outside the relation (shared slots consistent)
                    asg = {}
                    consistent = True
                    for v, b in zip(vs, x):
                        if asg.setdefault(v, b) != b:
                            consistent = False
                    if consistent and x not in allowed:
                        cl.append([-(v + 1) if b else (v + 1) for v, b in asg.items()])
            else:
                named = []
                for v in vs:                                             # break collisions with tied fresh copies
                    if v in named:
                        c = fresh(); eq(v, c); named.append(c)
                    else:
                        named.append(v)
                fmap = {}
                for k in gadget:
                    ids = []
                    for u in k:
                        if u < 4:
                            ids.append(named[u])
                        else:
                            ids.append(fmap.setdefault(u, fresh()))
                    nae(*ids)
    last = rows[-1]
    for i in range(len(last) - 2):
        nae(last[i], last[i + 1], last[i + 2])
    return cl


def alive_seq(parity_slots, gadget=None, rel=None, T=TMAX):
    out = []
    for t in range(1, T + 1):
        with Solver(name="cadical153", bootstrap_with=growth(t, parity_slots, gadget, rel)) as s:
            out.append(s.solve())
    return out


def classify(seq, pmax=16, amax=32):
    if all(x == seq[0] for x in seq):
        return "constant"
    for p in range(1, pmax + 1):
        for a in range(amax):
            if all(seq[t] == seq[t + p] for t in range(a, len(seq) - p)):
                return "eventually constant" if p == 1 else f"period {p}"
    return "unexplained"


RULES = {"rule 60": ["n0", "o-1", "o0", "r"], "rule 90": ["n0", "o-1", "o+1", "r"], "rule 150": ["n0", "o-1", "o0", "o+1"],
         "rule 102": ["n0", "o0", "o+1", "r"], "hop": ["n0", "oh", "o0", "r"]}


def s2():
    S1 = json.load(open(os.path.join(OUT, "s1.json")))
    g = [tuple(k) for k in S1["table"][str(S1["least_f"])]["gadget"]]
    out = {}
    for name, slots in RULES.items():
        direct = alive_seq(slots)
        via = alive_seq(slots, gadget=g) if name in ("rule 60", "hop") else None
        out[name] = dict(direct="".join("1" if a else "0" for a in direct), gadget_equal=(via == direct) if via is not None else None,
                         alive_depths=[t + 1 for t, a in enumerate(direct) if a][:40], cls=classify(direct))
        print(name, out[name]["cls"], out[name]["gadget_equal"], out[name]["direct"], flush=True)
    json.dump(out, open(os.path.join(OUT, "s2.json"), "w"), indent=1)


def s3(worker, workers):
    S1 = json.load(open(os.path.join(OUT, "s1.json")))
    f = S1["least_f"]
    g = [tuple(k) for k in S1["table"][str(f)]["gadget"]]
    n = 4 + f
    allk = [k for k in itertools.combinations(range(n), 3) if not all(v < 4 for v in k)]
    mutants = [("delete", j, None) for j in range(len(g))] + [("replace", j, k) for j in range(len(g)) for k in allk if k not in g]
    even = {x for x in itertools.product((0, 1), repeat=4) if sum(x) % 2 == 0}
    f_out = open(os.path.join(OUT, f"s3_{worker}.jsonl"), "w")
    for idx, (kind, j, k) in enumerate(mutants):
        if idx % workers != worker:
            continue
        mg = [x for i, x in enumerate(g) if i != j] + ([k] if k else [])
        rel = projection(4, f, mg)
        if rel == even:
            seq, cls = None, "same parity"
        else:
            seq = alive_seq(RULES["rule 60"], rel=rel)
            cls = classify(seq)
        f_out.write(json.dumps(dict(kind=kind, j=j, k=k, rel_size=len(rel), cls=cls,
                                    alive="".join("1" if a else "0" for a in seq) if seq else None)) + "\n")
        f_out.flush()
    f_out.close()


def summarize():
    S1 = json.load(open(os.path.join(OUT, "s1.json")))
    S2 = json.load(open(os.path.join(OUT, "s2.json")))
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(OUT, "s3_*.jsonl"))) for x in open(n)]
    f, m = S1["least_f"], S1["least_m"]
    S = dict(table={k: v["m"] for k, v in S1["table"].items()}, least_f=f, least_m=m,
             minimal_gadgets=S1["minimal_gadgets_at_least_f"], enumeration_complete=S1["enumeration_complete"])
    S["P1_plateau"] = S1["table"]["5"]["m"] == S1["table"]["6"]["m"]
    S["G_gadget_equals_direct"] = {k: v["gadget_equal"] for k, v in S2.items() if v["gadget_equal"] is not None}
    S["rules"] = {k: dict(cls=v["cls"], alive_depths=v["alive_depths"][:30]) for k, v in S2.items()}
    counts = lambda r: r["cls"] == "same parity" or r["cls"] == "unexplained"
    S["mutants"] = len(rows)
    S["mutant_classes"] = dict(Counter(r["cls"] for r in rows))
    S["P2_fragility_share_counting"] = round(sum(counts(r) for r in rows) / len(rows), 4) if rows else None
    # weight share of counting descriptions under the code of the row language with h helpers per position
    h = f
    rel_n = 5 * (1 + h) + 1
    C = math.comb(rel_n, 3)
    gamma = lambda n: 2 * int(math.floor(math.log2(n))) + 1
    bits = gamma(h) + gamma(m + 1) + math.log2(math.comb(C, m))
    n_desc = S1["minimal_gadgets_at_least_f"] * 3                  # rules 60, 90, 150, each by any minimal labelled gadget
    S["description_bits"] = round(bits, 2)
    S["counting_descriptions_found"] = n_desc
    S["weight_share_log2"] = round(math.log2(n_desc) - bits, 2)
    S["distinctions_per_position"] = 1 + f
    return S


if __name__ == "__main__":
    a = sys.argv[1]
    if a == "--s1":
        s1()
    elif a == "--s2":
        s2()
    elif a == "--s3":
        s3(int(sys.argv[2]), int(sys.argv[3]))
    elif a == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))

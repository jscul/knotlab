"""Rebuild ordinary parity growth from the census input, then check the stored rows."""
import argparse
from collections import Counter, defaultdict
from functools import reduce
import gzip
from itertools import combinations
import json
from operator import xor
from pathlib import Path
from random import Random

import networkx as nx

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
STARTS = STUDY.parent / "FORBID-EDITS-20261126-001" / "starts.json"


def mask(entries):
    return sum(1 << i for i in entries)


def supports(row):
    count, sharing, loose = row
    owners = [(a, b) for a, b, n in sharing for _ in range(n)]
    owners.extend((k,) for k, n in enumerate(loose) for _ in range(n))
    return [tuple(d for d, hs in enumerate(owners) if k in hs) for k in range(count)]


def holders(knots):
    held = defaultdict(set)
    for k, ds in enumerate(knots):
        for d in ds:
            held[d].add(k)
    assert all(1 <= len(hs) <= 2 for hs in held.values())
    return held


def groups(knots, eligible):
    """Choose maximal eligible groups with pairwise witnesses but no shared witness."""
    meets = [set() for _ in knots]
    for hs in holders(knots).values():
        if len(hs) == 2:
            a, b = hs
            meets[a].add(b)
            meets[b].add(a)
    pairs = {p for p in combinations(sorted(eligible), 2) if meets[p[0]] & meets[p[1]]}
    candidates = nx.Graph()
    candidates.add_edges_from(pairs)
    large = sorted(tuple(sorted(g)) for g in nx.find_cliques(candidates)
                   if len(g) >= 3 and not set.intersection(*(meets[k] for k in g)))
    covered = {pair for g in large for pair in combinations(g, 2)}
    return large + sorted(pairs - covered)


def proposal(knots):
    held = holders(knots)
    loose = {k: [d for d in ds if len(held[d]) == 1] for k, ds in enumerate(knots)}
    live = [k for k, ds in loose.items() if ds]
    if not live:
        return "closed", []
    plan = groups(knots, live)
    demand = Counter(k for g in plan for k in g)
    if any(demand[k] > len(loose[k]) for k in live):
        return "stalled", []
    for k in live:
        plan.extend([(k,)] * (len(loose[k]) - demand[k]))
    supply = {k: iter(loose[k]) for k in live}
    inputs = [tuple(sorted(next(supply[k]) for k in g)) for g in plan]
    return "funded", inputs


def advance(knots, inputs):
    # On this connected census a sum of old knots supported only on loose
    # distinctions includes both holders of each shared distinction, or neither.
    # Thus a nonempty selection of loose inputs is implied iff it is all loose inputs.
    held = holders(knots)
    loose = {d for d, hs in held.items() if len(hs) == 1}
    assert Counter(d for ds in inputs for d in ds) == Counter(loose)
    assert all(len(set.union(*(held[d] for d in ds))) == len(ds) for ds in inputs)
    additions = range(len(knots), len(knots) + len(inputs))
    demand = Counter(k for g in groups(knots + inputs, additions) for k in g)
    fresh = max(held) + 1
    out = knots.copy()
    for k, ds in zip(additions, inputs, strict=True):
        n = demand[k] if set(ds) == loose else max(demand[k], 1, 3 - len(ds))
        out.append(ds + tuple(range(fresh, fresh + n)))
        fresh += n
    return out


class Reading:
    def __init__(self, knots):
        self.held = holders(knots)
        self.knots = knots
        self.loose = [{d for d in ds if len(self.held[d]) == 1} for ds in knots]
        self.masks = [mask(ds) for ds in knots]
        self.anti = {d: mask(f for f, fs in self.held.items() if not hs & fs)
                     for d, hs in self.held.items()}
        self.anti_knot = [reduce(xor, (self.anti[d] for d in ds), 0) for ds in knots]
        self.sign = {p: (self.anti_knot[p[0]] & self.masks[p[1]]).bit_count() % 2
                     for p in combinations(range(len(knots)), 2)}

    def forced_and_open(self, terminal):
        state = {}
        for (a, b), s in self.sign.items():
            n = 0 if terminal else len(self.loose[a]) * len(self.loose[b])
            state[a, b] = ("open" if n else ("fail" if s else "commute"), n)
        return state

    def signed_products(self, count, signs):
        """Return signs of every ordered monomial in the signed knot group."""
        laws = {(0, 0)}
        for ds, s in zip(self.knots[:count], signs[:count], strict=True):
            step = set()
            for word, old in laws:
                sign = s ^ old
                for d in sorted(ds):
                    sign ^= ((word >> (d + 1)) & (self.anti[d] >> (d + 1))).bit_count() % 2
                    word ^= 1 << d
                step.add((word, sign))
            laws |= step
        return laws


def closer(read, sizes, stats):
    n = sizes[-1]
    signs = [0] * n
    unsigned = read.signed_products(n, signs)
    # Each distinction has two holders in one connected closure. Only the
    # empty selection and all knots have empty support.
    odd = int((0, 1) in unsigned)
    signs[-1] = odd
    laws = read.signed_products(n, signs)
    assert (0, 1) not in laws
    signed = dict(laws)
    candidates = nx.Graph()
    candidates.add_nodes_from(read.held)
    for ds in read.knots:
        candidates.add_edges_from(combinations(ds, 2))
    contexts = [mask(ds) for ds in nx.find_cliques(candidates)]
    mismatches = 0
    classical = {(0, 0)}
    for ds, s in zip(read.masks, signs, strict=True):
        classical |= {(w ^ ds, q ^ s) for w, q in classical}
    for p in contexts:
        mismatches += any(w and (w & ~p) == 0 and signed[w] != q for w, q in classical)
    for size in sizes[:-1]:
        earlier = read.signed_products(size, signs)
        assert earlier <= laws
        if earlier == laws:
            stats["earlier stages generate full signed group"] += 1
        old = reduce(int.__or__, read.masks[:size], 0)
        for p in contexts:
            q = p & old
            if q:
                stats["earlier maximal-set restrictions tested"] += 1
                assert not any(w & ~q == 0 for w, s in laws - earlier)
    return {"forced sign": "odd" if odd else "even", "GF(2) reader contradicted": mismatches}


def replay(knots, stats):
    history = []
    birth_round = [0] * len(knots)
    for t in range(5):
        status, inputs = proposal(knots)
        terminal = status != "funded"
        read = Reading(knots)
        state = read.forced_and_open(terminal)
        if t:
            prev, old_state, _, _ = history[-1]
            added = knots[len(prev.knots):]
            kids = [set.union(*(prev.held[d] for d in ds if d in prev.held)) for ds in added]
            for d, hs in prev.held.items():
                assert len(read.held[d]) == 2
                # No settled pair changes, including already co-held loose pairs.
                if len(hs) == 2:
                    assert read.held[d] == hs
                    assert not (prev.anti[d] ^ read.anti[d]) & mask(prev.held)
            for pair, old_sign in prev.sign.items():
                a, b = pair
                children = sum(a in parents and b in parents for parents in kids)
                predicted = birth_round[a] == birth_round[b] == t - 1 and children % 2 == 1
                changed = read.sign[pair] != old_sign
                assert changed == predicted
                assert not changed or old_state[pair][0] == "open"
                stats["knot pair comparisons"] += 1
                if changed:
                    stats["changes"] += 1
                    stats["commuting to failing" if read.sign[pair] else "failing to commuting"] += 1
        history.append((read, state, terminal, t))
        if terminal or t == 4:
            break
        grown = advance(knots, inputs)
        birth_round.extend([t + 1] * (len(grown) - len(knots)))
        knots = grown

    if status == "stalled":
        stats["stalled at the start"] += len(history) == 1
        if any(v[0] == "fail" for v in read.forced_and_open(False).values()):
            stats["stalls with a failure even if loose pairs stay open"] += 1
    first_failure = next((t for _, s, _, t in history if any(v[0] == "fail" for v in s.values())), None)
    ending = status if terminal else "growing"
    tally = Counter(v[0] for v in state.values())
    b3 = []
    for (old, old_state, _, t), (new, _, _, _) in zip(history, history[1:]):
        # A loose pair belongs to exactly one pair of holders, so the parity
        # equations for the open pairs have disjoint unknowns. Each row with
        # n > 0 unknowns has 2**(n-1) solutions.
        exists = all(name != "fail" for name, _ in old_state.values())
        unique = exists and all(n <= 1 for _, n in old_state.values())
        realised = all(new.sign[p] == 0 for p in old.sign)
        b3.append({"round": t, "open pairs": sum(n for _, n in old_state.values()),
                   "a choice exists": exists, "unique": unique, "next round realises one": realised})
    answer = {"rounds": len(history) - 1, "end": ending, "knots": len(knots),
              "B1 first round with a settled failing pair": first_failure,
              "B1 knot pairs at the end": dict(tally), "B3": b3}
    if ending == "closed":
        sizes = [len(old.knots) for old, _, _, _ in history]
        answer["B4"] = "knots do not commute" if tally["fail"] else closer(read, sizes, stats)
    return answer


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--limit", type=int, default=300, choices=range(1, 301), metavar="N")
    arg.add_argument("--named", action="store_true")
    args = arg.parse_args()
    if args.named:
        starts = {
            "ring of three, one loose each": [(0, 1, 2), (1, 3, 4), (3, 0, 5)],
            "four mutually meeting knots, one loose each": [(0, 1, 2, 6), (0, 3, 4, 7), (1, 3, 5, 8), (2, 4, 5, 9)],
            "one knot of three places": [(0, 1, 2)],
            "one knot of four places": [(0, 1, 2, 3)],
            "two knots of four and three places sharing one": [(0, 1, 2, 3), (0, 4, 5)],
        }
        records = "part_b_named.jsonl.gz"
    else:
        census = json.loads(STARTS.read_text())
        assert len(census) == 7075
        sample = sorted(Random(20261128).sample(range(len(census)), 300))
        starts = {i: supports(census[i]) for i in sample[:args.limit]}
        records = "part_b_census.jsonl.gz"
    total = Counter()
    computed = {}
    for i, start in list(starts.items())[:args.limit]:
        stats = Counter()
        result = replay(start, stats)
        result["B2"] = ({"changes": stats["changes"], "changes predicted by the formula": stats["changes"],
                         "formula wrong": 0} if result["rounds"] else {})
        computed[i] = result
        total.update(stats)
        end = result["end"]
        t = result["B1 first round with a settled failing pair"]
        total[end] += 1
        total[f"{end}, first settled failure {t}"] += 1
        if t is not None:
            total["starts with permanent failure"] += 1
        if isinstance(result.get("B4"), dict):
            total[result["B4"]["forced sign"] + " commuting closers"] += 1
        for row in result["B3"]:
            group = "before failure" if t is None or row["round"] < t else "at or after failure"
            total[group] += 1
            for flag in ("a choice exists", "unique", "next round realises one"):
                total[group + ", " + flag] += row[flag]
        if args.named and i == "two knots of four and three places sharing one":
            _, inputs = proposal(start)
            grown = advance(start, inputs)
            before, after = Reading(start), Reading(grown)
            assert before.sign[0, 1] == after.sign[0, 1] == 0
            assert after.forced_and_open(False)[0, 1][0] == "commute"
            assert all(len(ds) == 1 for ds in inputs)
        if args.named and i == "one knot of four places":
            _, inputs = proposal(start)
            grown = advance(start, inputs)
            assert [len(ds) for ds in grown] == [4] * 5
            assert Reading(grown).forced_and_open(False)[0, 1][0] == "fail"
        if args.named and i == "ring of three, one loose each":
            _, inputs = proposal(start)
            grown = advance(start, inputs)
            assert list(Reading(start).sign.values()) == [1, 1, 1]
            assert not any(Reading(grown).sign.values()) and len(inputs) == 1
    with gzip.open(STUDY / records, "rt") as f:
        stored = {row["start"]: row for row in map(json.loads, f)}
    if args.limit == 300:
        assert computed.keys() == stored.keys()
    for i, computed_row in computed.items():
        assert computed_row == {k: v for k, v in stored[i].items() if k != "start"}, (i, computed_row, stored[i])
    print(json.dumps({"compared rows": len(computed), **dict(sorted(total.items()))}, indent=2))


if __name__ == "__main__":
    main()

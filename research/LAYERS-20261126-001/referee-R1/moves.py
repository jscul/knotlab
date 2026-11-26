"""Independent ordinary parity growth, moves, and one-holder readings."""

import argparse
import itertools
import json
import math
import random
import resource
import time
from collections import Counter, defaultdict, deque
from functools import reduce
from operator import or_
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
ROSTER = SOURCE.parent / "FORBID-EDITS-20261126-001" / "starts.json"
BOUNDS = (3, 4, 5, 6)


def bits(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def mask(ids):
    return sum(1 << i for i in ids)


def dot(a, b):
    return (a & b).bit_count() % 2


def add(basis, word):
    while word:
        leading = word.bit_length() - 1
        if leading not in basis:
            basis[leading] = word
            return True
        word ^= basis[leading]
    return False


def echelon(words):
    answer = {}
    for word in words:
        add(answer, word)
    return answer


def perp(words, n):
    pivots = echelon(words)
    rows = sorted(pivots.items())
    answer = []
    for free in sorted(set(range(n)) - pivots.keys()):
        word = 1 << free
        for pivot, row in rows:
            if dot(word, row):
                word |= 1 << pivot
        answer.append(word)
    return answer


def values(words, basis):
    return [sum(dot(word, row) << j for j, row in enumerate(basis)) for word in words]


def all_words(basis):
    words = [0]
    for word in basis:
        words += [w ^ word for w in words]
    return words


def restrict(word, ids):
    return sum(((word >> i) & 1) << j for j, i in enumerate(ids))


def owners(supports):
    table = defaultdict(list)
    for h, support in enumerate(supports):
        for i in support:
            table[i].append(h)
    assert all(len(group) in (1, 2) for group in table.values())
    assert sorted(table) == list(range(len(table)))
    return table


def meetings(supports):
    table = owners(supports)
    nb = [set() for _ in supports]
    for group in table.values():
        if len(group) == 2:
            a, b = group
            nb[a].add(b)
            nb[b].add(a)
    return nb


def parent_groups(nb, live):
    """Maximal mutually eligible sets which have no single common holder."""
    eligible = {a: set() for a in live}
    for neighbors in nb:
        for a, b in itertools.combinations(neighbors & eligible.keys(), 2):
            eligible[a].add(b)
            eligible[b].add(a)
    large = []

    def maximal(chosen, left, visited):
        if not left and not visited:
            if len(chosen) >= 3 and not any(chosen <= ns for ns in nb):
                large.append(tuple(sorted(chosen)))
            return
        pivot = max(left | visited, key=lambda a: len(left & eligible[a]))
        for a in sorted(left - eligible[pivot]):
            maximal(chosen | {a}, left & eligible[a], visited & eligible[a])
            left.remove(a)
            visited.add(a)

    if live:
        maximal(set(), set(live), set())
    singles = {(a, b) for a in live for b in eligible[a] if a < b}
    for group in large:
        singles.difference_update(itertools.combinations(group, 2))
    return sorted(large) + sorted(singles)


def grow(supports):
    own = owners(supports)
    free = {h: deque(i for i in s if len(own[i]) == 1) for h, s in enumerate(supports)}
    live = {h for h, loose in free.items() if loose}
    if not live:
        return None, "closed"
    groups = parent_groups(meetings(supports), live)
    demand = Counter(h for group in groups for h in group)
    if any(demand[h] > len(free[h]) for h in live):
        return None, "stalled"
    payments = [tuple(free[h].popleft() for h in group) for group in groups]
    payments.extend((i,) for h in sorted(live) for i in free[h])
    scratch = supports + payments
    newborns = set(range(len(supports), len(scratch)))
    next_groups = parent_groups(meetings(scratch), newborns)
    demand = Counter(h for group in next_groups for h in group)
    laws = echelon(map(mask, supports))
    comp = []
    next_id = len(own)
    for h in sorted(newborns):
        paid = scratch[h]
        implied = not add(laws.copy(), mask(paid))
        fresh = demand[h] if implied else max(demand[h], 1, 3 - len(paid))
        comp.append(paid + tuple(range(next_id, next_id + fresh)))
        next_id += fresh
    return supports + comp, "funded"


def make_supports(n, pairs, loose):
    supports = [[] for _ in range(n)]
    d = 0
    for a, b, multiplicity in pairs:
        for _ in range(multiplicity):
            supports[a].append(d)
            supports[b].append(d)
            d += 1
    for h, count in enumerate(loose):
        supports[h].extend(range(d, d + count))
        d += count
    return [tuple(s) for s in supports]


def literal_cycle_controls(supports, space, generators):
    """Independent test by visiting every allowed change on the selected small stages."""
    words = [w for w in all_words(space) if w]
    lim = max(BOUNDS)
    minima = [math.inf] * len(owners(supports))
    for w in words:
        for i in bits(w):
            minima[i] = min(minima[i], w.bit_count())
    controls = {"through": [w for w in words if any(minima[i] == w.bit_count() for i in bits(w))]}
    controls.update({b: [w for w in words if w.bit_count() <= b] for b in BOUNDS})
    for k, wds in controls.items():
        span = echelon(generators[k])
        assert all(not add(span.copy(), w) for w in wds)
        assert len(echelon(wds)) == len(span)
    return len(words) + 1


def cycle_generators(supports):
    """Use even changes as cycles of the classical incidence multigraph."""
    own = owners(supports)
    outside = len(supports)
    adj = [[] for _ in range(outside + 1)]
    end = []
    for i in range(len(own)):
        a, b = (own[i] + [outside])[:2]
        adj[a].append((b, i))
        adj[b].append((a, i))
        end.append((a, b))

    # Each simple cycle has a least holder. Permit both directions and deduplicate
    # by support. Distinct parallel distinctions therefore give length-two cycles.
    found = set()
    for base in range(len(adj)):
        def extend(h, seen, used, length):
            for j, i in adj[h]:
                if used & (1 << i):
                    continue
                nxt = used | (1 << i)
                if j == base:
                    found.add(nxt)
                elif length + 1 < max(BOUNDS) and j > base and not (seen >> j) & 1:
                    extend(j, seen | (1 << j), nxt, length + 1)
        extend(base, 1 << base, 0, 0)
    by_size = sorted(found, key=lambda w: (w.bit_count(), w))
    through = set()
    shortest = [math.inf] * len(own)
    for w in by_size:
        weight = w.bit_count()
        has_shortest = False
        for i in bits(w):
            if shortest[i] >= weight:
                shortest[i] = weight
                has_shortest = True
        if has_shortest:
            through.add(w)

    # A distinction with a larger minimum needs its own unrestricted search.
    for i, (a, b) in enumerate(end):
        if shortest[i] < math.inf:
            continue
        dist = {b: 0}
        queue = deque([b])
        while queue:
            h = queue.popleft()
            for j, d in adj[h]:
                if d != i and j not in dist:
                    dist[j] = dist[h] + 1
                    queue.append(j)
        if a not in dist:
            continue
        shortest[i] = dist[a] + 1
        desc = [(a, 1 << i)]
        while desc:
            h, used = desc.pop()
            if h == b:
                through.add(used)
            else:
                desc.extend((j, used | (1 << d)) for j, d in adj[h]
                            if d != i and dist.get(j, math.inf) == dist[h] - 1)
    generators = {"through": sorted(through)}
    generators.update({b: [w for w in by_size if w.bit_count() <= b] for b in BOUNDS})
    return generators, [None if w == math.inf else w for w in shortest]


def knot_ranks(supports, space, moves):
    """Per holder obtain every label supported there; then take their union's span."""
    local = []
    actual_knots = []
    one = []
    for h, ids in enumerate(supports):
        places = mask(ids)
        restricted = [restrict(w & places, ids) for w in moves]
        candidates = [mask(ids[j] for j in bits(sol)) for sol in perp(restricted, len(ids))]
        proj = len(echelon(w & places for w in space))
        k123 = len(ids) >= 3 and proj == len(ids) - 1
        if k123:
            actual_knots.append(h)
        one.append(len(echelon(values(candidates, space))))
        local.extend(candidates)
    return local, actual_knots, one


def classify(supports, space, moves, selected=(), verbose=False):
    n = len(owners(supports))
    basis = list(echelon(moves).values())
    labels = len(space) - len(basis)
    local, actual, local_dims = knot_ranks(supports, space, basis)
    span = echelon(values(local, space))
    gl = labels - len(span)
    covered = reduce(or_, basis, 0)
    record = {"label_bits": labels, "single_holder_span": len(span), "whole_bits": gl,
              "mobile": covered.bit_count(), "move_span": len(basis),
              "simple_generators": len(moves), "holders_passing_knot_test": len(actual)}
    if selected:
        sigs = [[dot(label, w) for w in basis] for label in selected]
        surviving = [not any(image) and any(dot(label, w) for w in space)
                     for label, image in zip(selected, sigs)]
        record["named_parities_are_labels"] = surviving
        named_mod_local = span.copy()
        for v, yes in zip(values(selected, space), surviving):
            if yes:
                add(named_mod_local, v)
        record["named_labels_independent_mod_single_holder"] = len(named_mod_local) - len(span)
    if verbose and gl:
        whole = []
        for l in sorted(perp(basis, n), key=lambda x: (x.bit_count(), x)):
            if add(span, values([l], space)[0]):
                whole.append(l)
        assert len(whole) == gl
        # Show an allowed change toggling each named label alone.
        answers = {}
        for idx, v in enumerate(space):
            signature = mask(j for j, l in enumerate(whole) if dot(l, v))
            state = v
            while signature:
                p = signature.bit_length() - 1
                if p not in answers:
                    answers[p] = (signature, state)
                    break
                smaller, companion = answers[p]
                signature ^= smaller
                state ^= companion
        exchanges = []
        for j in range(gl):
            target, state = 1 << j, 0
            while target:
                v, change = answers[target.bit_length() - 1]
                target ^= v
                state ^= change
            exchanges.append(list(bits(state)))
        record.update({"whole_label_basis_mod_local": [list(bits(l)) for l in whole],
                       "independent_allowed_exchanges": exchanges})
    if verbose:
        record["single_holder_label_bits"] = local_dims
        record["fixed_under_moves"] = list(bits(((1 << n) - 1) ^ covered))
        record["holders_failing_knot_test"] = sorted(set(range(len(supports))) - set(actual))
    return record


def inspect_stage(supports, selected=(), verbose=False, literal=False):
    start = time.perf_counter()
    n = len(owners(supports))
    space = perp(map(mask, supports), n)
    generators, mins = cycle_generators(supports)
    out = {str(k): classify(supports, space, w, selected, verbose) for k, w in generators.items()}
    controls = None
    if literal:
        controls = literal_cycle_controls(supports, space, generators)
    return {"knots": len(supports), "distinctions": n, "allowed_bits": len(space),
            "shortest_through_distinction": dict(Counter(map(str, mins))),
            "literal_control_assignments": controls, "move_rules": out,
            "seconds": round(time.perf_counter() - start, 5)}


def replay_archive(args):
    direct = json.loads(ROSTER.read_text())
    ids = {}
    ans = []
    for kind in ("census", "heldout"):
        data = [json.loads(s) for s in (SOURCE / f"frozen_{kind}.jsonl").read_text().splitlines()]
        ids[kind] = [r["index"] for r in data if r.get("classes", 0) >= 4]
    required = {int(k.split("-")[0]): set() for k in ids["heldout"]}
    for key in ids["heldout"]:
        n, idx = map(int, key.split("-"))
        required[n].add(idx)
    selected = [(f"census-{i}", direct[i]) for i in ids["census"]]
    if not args.pilot:
        for n, positions in sorted(required.items()):
            rng = random.Random(20261206 + n)
            pairs = list(itertools.combinations(range(n), 2))
            j = -1
            while j < max(positions):
                meeting = [p for p in pairs if rng.random() < 1 / 3]
                mult = [(*p, rng.choice((1, 2))) for p in meeting]
                loose = [rng.choice((0, 1, 2)) for _ in range(n)]
                if sum(m for _, _, m in mult) + sum(loose) > 18:
                    continue
                supports = make_supports(n, mult, loose)
                if min(map(len, supports)) < 3:
                    continue
                nb = meetings(supports)
                seen, stack = {0}, [0]
                while stack:
                    h = stack.pop()
                    new = nb[h] - seen
                    seen |= new
                    stack.extend(new)
                if len(seen) != n:
                    continue
                j += 1
                if j in positions:
                    selected.append((f"heldout-{n}-{j}", (n, mult, loose)))
    for key, spec in selected[:1] if args.pilot else selected:
        before = make_supports(*spec)
        after, status = grow(before)
        assert status == "funded"
        stage = inspect_stage(after, verbose=True, literal=True)
        assert stage["move_rules"]["through"]["label_bits"] == 2
        ans.append({"archive": key, "source_knots": spec[0], "grown_supports": after, "grown": stage})
    return ans


def joined_rings(lengths, joins, live_mode="all", minimum=2):
    # Shared distinctions are assigned first, in cyclic order inside each ring.
    offsets = [sum(lengths[:k]) for k in range(len(lengths))]
    permanent = [(off + j, off + (j + 1) % length, 1)
                 for length, off in zip(lengths, offsets) for j in range(length)]
    ring_parities = [mask(range(off, off + length)) for length, off in zip(lengths, offsets)]
    count = sum(lengths)
    parent = list(range(count))

    def root(a):
        while a != parent[a]:
            a = parent[a]
        return a

    marks = set()
    passive = set()
    added = []
    for a, b, kind, length, copies in joins:
        marks.update((a, b))
        if kind == "shared_holder":
            parent[root(b)] = root(a)
        else:
            middle = list(range(count, count + length))
            passive.update(middle)
            count += length
            path = [a] + middle + [b]
            added.extend((u, v, copies) for u, v in zip(path, path[1:]))
    alias = {a: root(a) if a < len(parent) else a for a in range(count)}
    names = {a: i for i, a in enumerate(sorted(set(alias.values())))}
    def identify(a):
        return names[alias[a]]
    edges = [(identify(a), identify(b), m) for a, b, m in permanent + added]
    n = len(names)
    passive = {identify(h) for h in passive}
    marks = {identify(h) for h in marks}
    if live_mode == "all":
        live = set(range(n))
    elif live_mode == "rings":
        live = set(range(n)) - passive
    elif live_mode == "except_joins":
        live = set(range(n)) - passive - marks
    else:
        raise ValueError(live_mode)
    base = make_supports(n, edges, [0] * n)
    groups = parent_groups(meetings(base), live)
    demand = Counter(h for g in groups for h in g)
    loose = [max(minimum, demand[h], 3 - len(base[h])) if h in live else 0 for h in range(n)]
    if any(len(s) + x < 3 for s, x in zip(base, loose)):
        return None, []
    return make_supports(n, edges, loose), ring_parities


def patterns():
    yield "single_5", [5], [], "all"
    yield "apart_5_5", [5, 5], [], "all"
    yield "shared_holder_5_5", [5, 5], [(0, 5, "shared_holder", 0, 1)], "all"
    for lengths in ([5, 5], [4, 4], [5, 7]):
        a, b = lengths
        for mode in ("all", "rings", "except_joins"):
            for joins in (1, 2):
                for inner in (0, 1, 2, 3):
                    for copies in (1, 2):
                        if mode != "all" and inner and copies == 1:
                            continue
                        if mode == "rings" and not inner:
                            continue
                        links = [(0, a, "change", inner, copies)]
                        if joins == 2:
                            links.append((a // 2, a + b // 2, "change", inner, copies))
                        name = f"{a}_{b}_joins{joins}_inside{inner}_copies{copies}_{mode}"
                        yield name, lengths, links, mode


def original_ring_patterns():
    """The two built-start lists in the study plus its single-ring sizes three to seven."""
    for n in (3, 4, 5, 6, 7):
        yield f"single_{n}", [n], [], "all"
    for (a, b), joins in [
        ((5, 5), ("same", "touch", "one", "two")),
        ((4, 4), ("touch",)),
        *((pair, ("apart", "same", "touch", "one"))
          for pair in ((3, 5), (5, 7), (7, 7), (3, 3), (4, 6), (5, 6))),
    ]:
        for j in joins:
            if j == "apart":
                links = []
            elif j == "same":
                links = [(0, a, "shared_holder", 0, 1)]
            else:
                links = [(0, a, "change", {"touch": 0, "one": 1, "two": 2}[j], 1)]
            yield f"rings_{a}_{b}_{j}", [a, b], links, "all"
    for (a, b, c), modes in [
        ((5, 5, 5), ("apart", "same", "path", "cycle")),
        ((3, 5, 7), ("apart", "same", "path")),
        ((4, 4, 4), ("cycle",)),
    ]:
        for mode in modes:
            if mode == "apart":
                links = []
            elif mode == "same":
                links = [(0, a, "shared_holder", 0, 1), (0, a + b, "shared_holder", 0, 1)]
            else:
                links = [(0, a, "change", 0, 1), (a + 2, a + b, "change", 0, 1)]
                if mode == "cycle":
                    links.append((a + b + 2, 2, "change", 0, 1))
            yield f"rings_{a}_{b}_{c}_{mode}", [a, b, c], links, "all"


def replay_rings(args):
    ans = []
    candidates = original_ring_patterns() if args.group == "original-rings" else patterns()
    for name, lengths, joins, live in candidates:
        if args.case and name not in args.case:
            continue
        if args.pilot and name not in ("single_5", "5_5_joins2_inside2_copies2_rings", "rings_5_5_5_same"):
            continue
        before, labels = joined_rings(lengths, joins, live)
        if before is None:
            continue
        stages = []
        stage = before
        for r in range(args.rounds + 1):
            found = inspect_stage(stage, labels, args.verbose, literal=r == 0 and len(lengths) == 1)
            stages.append(found)
            if r < args.rounds:
                stage, status = grow(stage)
                if not stage:
                    break
        item = {"pattern": name, "source_ring_lengths": lengths, "joins": joins, "funding": live, "stages": stages}
        if args.verbose:
            item["source_supports"] = before
            item["last_stage_supports"] = stage
        ans.append(item)
    return ans


def replay_candidate(args):
    records = json.loads((HERE / "extended_witness.json").read_text())
    selected = next(r for r in records if r["sample index"] == "10-34" and r["cohort"] == "larger sample")
    stage = [tuple(s) for s in selected["start supports"]]
    initial = stage
    labels = list(map(mask, selected["two parities over start distinctions"]))
    stages = []
    limit = min(1, args.rounds) if args.pilot else args.rounds
    for r in range(limit + 1):
        stages.append(inspect_stage(stage, labels, args.verbose))
        if r < limit:
            stage, status = grow(stage)
            assert status == "funded"
    return [{"meaning": "a ten-knot result from the referee's independent larger-start sample",
             "sample_index": selected["sample index"], "source_supports": initial, "stages": stages}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=("archive", "rings", "original-rings", "candidate"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--case", nargs="*")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    now = time.perf_counter()
    replay = {"archive": replay_archive, "rings": replay_rings, "original-rings": replay_rings,
              "candidate": replay_candidate}
    rows = replay[args.group](args)
    result = {"group": args.group, "pilot": args.pilot, "maximum_support_bounds": BOUNDS,
              "measured_seconds": round(time.perf_counter() - now, 5),
              "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "cases": rows}
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(len(rows), result["measured_seconds"], result["peak_resident_KiB"])


if __name__ == "__main__":
    main()

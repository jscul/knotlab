"""Challenge the holder, single-knot, padding and count-bound readings."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations, product
import json
import sys
import time

from census_replay import (
    HERE, VALID, Truth, advance, connected, inputs, labels,
    read_rows, stage_records,
)


def scalar_query(supports, law, C):
    """Enumerate assignments and keep literal states, even for a non-invariant law."""
    variables = sorted(set().union(*(set(s) for s in (*supports, *C))))
    bit = {v: 1 << k for k, v in enumerate(variables)}
    def mask(c):
        return sum(bit[x] for x in c)
    H, masks = tuple(map(mask, supports)), tuple(map(mask, C))
    present = Counter()
    deletion = [set() for h in H]
    by_knot = [{} for h in H]
    allowed_count = 0
    for state in range(1 << len(variables)):
        violations = [k for k, h in enumerate(H) if ((state & h).bit_count() & 1 if law == "parity"
                                                      else (state & h) in (0, h))]
        if len(violations) > 1:
            continue
        word = sum(1 << (2-i) for i, m in enumerate(masks) if (state & m) in (0, m))
        if violations:
            deletion[violations[0]].add(word)
        else:
            allowed_count += 1
            present[word] += 1
            for i, h in enumerate(H):
                by_knot[i].setdefault(state & h, set()).add(word)
    missing = set(range(8)) - present.keys()
    return {
        "allowed_states": allowed_count, "counts": {format(i, "03b"): present[i] for i in range(8)},
        "missing": [format(w, "03b") for w in sorted(missing)],
        "deletion_restores": [[format(w, "03b") for w in sorted(D & missing)] for D in deletion],
        "fixings": [{format(v, "b"): [format(w, "03b") for w in sorted(ws)] for v, ws in F.items()}
                    for F in by_knot],
    }


def literal_triplets(supports, law):
    """No holder or readability filter before tabulating all disjoint agreements."""
    xs = sorted(set().union(*map(set, supports)))
    possibilities = [c for w in (2, 3) for c in combinations(xs, w)]
    states = range(1 << len(xs))
    bit = {x: 1 << k for k, x in enumerate(xs)}
    hm = [sum(bit[x] for x in h) for h in supports]
    valid = tuple(s for s in states if all(not ((s & h).bit_count() & 1) for h in hm)) if law == "parity" else tuple(
        s for s in states if all((s & h) not in (0, h) for h in hm))
    counts = Counter()
    def readable(c):
        m = sum(bit[x] for x in c)
        return any(len(set(s & h for s in valid)) == len({(s & h, (s & m) in (0, m)) for s in valid}) for h in hm)
    read_at = {c: readable(c) for c in possibilities}
    found = []
    for C in combinations(possibilities, 3):
        if sum(map(len, C)) != len(set().union(*map(set, C))):
            continue
        counts["disjoint triples of carriers"] += 1
        unread = not any(read_at[c] for c in C)
        counts["all carriers unread at single knots"] += unread
        masks = tuple(sum(bit[x] for x in c) for c in C)
        image = {sum(1 << (2-i) for i, m in enumerate(masks) if (s & m) in (0, m)) for s in valid}
        missing = sum(1 << w for w in set(range(8)) - image)
        counts["passes joint-state test before single-knot filter"] += VALID[missing]
        if not unread or not VALID[missing]:
            continue
        counts["bonds"] += 1
        found.append((C, missing))
    return {"states": len(valid), "counts": dict(counts), "bonds": found}


def all_holders(supports, C, missing):
    # Keep the carrier variables even when no remaining law mentions them.
    result = []
    for size in range(1, len(supports) + 1):
        for H in combinations(range(len(supports)), size):
            sub = tuple(supports[k] for k in H)
            out = scalar_query(sub, "nae", C)
            if out["missing"] == missing and all(out["deletion_restores"]):
                result.append({"holders": H, "connected": connected(sub), "contains_carriers":
                               set().union(*map(set, C)) <= set().union(*map(set, sub))})
    return result


def knot_test(supports, C):
    """Submit the underlying laws and three defined readings, with the source distinctions forgotten."""
    sys.path.insert(0, str(HERE.parents[2] / "tools"))
    from knotlab.cli import main as check
    def clause(terms):
        return " ".join(terms)
    formula = []
    for support in supports:
        formula.extend(clause(f"{sign}d{x}" for x in support) for sign in ("", "~"))
    readings = "abc"
    for reading, carrier in zip(readings, C):
        for assignment in product((0, 1), repeat=len(carrier)):
            forbidden = [f"{'~' if bit else ''}d{x}" for x, bit in zip(carrier, assignment)]
            forbidden.append(reading if all(b == assignment[0] for b in assignment) else f"~{reading}")
            formula.append(clause(forbidden))
    witness = sorted({x for s in supports for x in s} | {x for c in C for x in c})
    output = []
    for r in readings:
        stream = StringIO()
        with redirect_stdout(stream):
            code = check(["check", "--cnf", "; ".join(formula), "--loops", *[s for s in readings if s != r],
                          "--contact", r, "--witnesses", *[f"d{x}" for x in witness], "--json"])
        assert code == 0
        result = json.loads(stream.getvalue())
        output.append({"contact": r, "is_knot": result["is_knot"], "binding": result["binding"],
                       "loss_on_erasure": result["loss_on_erasure"], "coexistence": result["coexistence"]})
    return output


def targeted(archive, limit):
    cases = {}
    support = archive[21]
    grown = advance(support)
    C = ((0, 5), (1, 6), (2, 3, 4))
    cases["single new knot on the one-loose three-knot source, archive rank 21"] = {
        "start": support, "stage": grown.supports, "births": [b.__dict__ for b in grown.births],
        "carriers": C, "literal_test": scalar_query(grown.supports, "nae", C),
        "minimal_sufficient_holders": all_holders(grown.supports, C, ["001"]),
        "all_disjoint_triples": literal_triplets(grown.supports, "nae"), "knot_test": knot_test(grown.supports, C),
    }
    if limit == 1:
        return cases
    ring = archive[17]
    places = tuple(x for h in ring for x in h if sum(x in other for other in ring) == 1)
    parity_states = [s for s in range(1 << 6) if all(sum((s >> x) & 1 for x in h) % 2 == 0 for h in ring)]
    implied = all(sum((s >> x) & 1 for x in places) % 2 == 0 for s in parity_states)
    assert implied and len(places) == 3
    stage = ring + (places,)
    cases["the even parity three-knot ring with one loose place per knot"] = {
        "before": ring, "possible_parent_groups": [[0, 1, 2]], "birth_inputs": places,
        "places_at_two_knots_after": all(sum(x in h for h in stage) == 2 for x in set().union(*map(set, stage))),
        "source_states": parity_states, "birth_already_implied_at_zero_fresh": implied,
        "round 0": literal_triplets(ring, "parity"), "round 1": literal_triplets(stage, "parity"),
    }
    closed = archive[477]
    cases["closed four-knot source with two missing words, archive rank 477"] = {
        "stage": closed, "direct": literal_triplets(closed, "nae"),
        "certificates": [dict(carriers=C, knot_test=knot_test(closed, C), **scalar_query(closed, "nae", C))
                         for C, missing in literal_triplets(closed, "nae")["bonds"]],
    }
    for rank, carriers in (
        (61, ((0, 1, 3), (2, 4, 7), (5, 6, 8))),
        (551, ((1, 4), (2, 3), (5, 6))),
    ):
        stage = archive[rank]
        cases[f"source rank {rank}"] = {
            "stage": stage, "carriers": carriers, "knot_test": knot_test(stage, carriers),
            "literal_test": scalar_query(stage, "nae", carriers),
        }
    stage = archive[589]
    C = ((0, 2, 4), (1, 6, 7), (3, 5, 8))
    cases["four-knot source with alternative holders, archive rank 589"] = {
        "stage": stage, "carriers": C, "literal_test": scalar_query(stage, "nae", C),
        "minimal_sufficient_holders": all_holders(stage, C, ["111"]),
    }
    return cases


def flip_allowed(T):
    def swap(cell, x):
        stride = 1 << (T.names.index(x) - 1)
        on = T.columns[x]
        return ((cell & on) >> stride) | ((cell & ~on) << stride)
    tables = {x: T.allowed & swap(T.allowed, x) for x in T.names[1:]}
    inverted = T.allowed
    for x in T.names[1:]:
        inverted = swap(inverted, x)
    tables[T.names[0]] = T.allowed & inverted
    return tables


def padding_records(C, T, missing):
    """Free one input by replacing it by a fresh distinction independent of the entire stage."""
    padding = []
    for i, c in enumerate(C):
        if len(c) == 2:
            # A free input to a pair can always set either output.
            continue
        bit = 4 >> i
        if any(missing & (1 << w) and not w & bit for w in range(8)):
            continue
        for x in c:
            core = tuple(v for v in c if v != x)
            reduced = tuple(core if j == i else cc for j, cc in enumerate(C))
            # For output one the core has to agree. For zero the fresh input can always disagree.
            absent_for_true = T.image(reduced) & sum(1 << w for w in range(8) if w & bit)
            if absent_for_true == missing:
                padding.append((i, x))
    return padding


def source_controls(archive, sample, ranks):
    totals, sample_totals, distribution, witnesses, cap_by_rank = Counter(), Counter(), Counter(), {}, []
    for rank in ranks:
        supports = archive[rank]
        T = Truth(supports)
        flips = flip_allowed(T)
        per_start = Counter()
        records = stage_records(supports, 4, connected_only=False, carry_reader=T)
        for C, (missing, certs, read) in records.items():
            held = [(H, m) for H, m in certs if connected(tuple(supports[k] for k in H))]
            any_good = [(H, m) for H, m in certs if m == missing and not read]
            if any_good and not any((H, m) in held for H, m in any_good):
                per_start["only disconnected minimal holders"] += 1
                witnesses.setdefault("only disconnected source holders", {
                    "rank": rank, "supports": supports, "carriers": C, "missing": labels(missing), "holders": any_good})
            if any_good:
                per_start["any sufficient set of at most four holders containing the carriers"] += 1
            if not held:
                continue
            H, m = held[0]
            if missing != m or read:
                continue
            per_start["registered definition"] += 1
            strict = all(len(set(c) & set(h)) <= 1 for c in C for h in supports)
            open_always = all(T.profile(c)[1] == 0 for c in C)
            single_flip = all(T.agreement(c) & flips[x] for c in C for x in c)
            independent_padding = padding_records(C, T, missing)
            if independent_padding:
                witnesses.setdefault("replace a carrier input by an independent distinction", {
                    "rank": rank, "supports": supports, "carriers": C, "missing": labels(missing),
                    "holders": H, "replacements": independent_padding})
            if strict:
                witnesses.setdefault("strict places", {
                    "rank": rank, "supports": supports, "carriers": C, "missing": labels(missing), "holders": H})
            if open_always:
                witnesses.setdefault("every carrier open under every single-knot fixing", {
                    "rank": rank, "supports": supports, "carriers": C, "missing": labels(missing), "holders": H})
            if not single_flip:
                witnesses.setdefault("carrier input cannot switch reading by a single allowed change", {
                    "rank": rank, "supports": supports, "carriers": C, "missing": labels(missing), "holders": H})
            per_start["at most one place per carrier at each knot"] += strict
            per_start["each carrier open under every single-knot fixing"] += open_always
            per_start["each input switches its reading in some permitted single-place change"] += single_flip
            per_start["at least one input can be replaced by an independent distinction"] += bool(independent_padding)
        for tot in [totals, sample_totals] if rank in sample else [totals]:
            tot["starts"] += 1
            for name, n in per_start.items():
                tot[name + ": bonds"] += n
                tot[name + ": starts"] += bool(n)
        distribution[str(per_start["registered definition"])] += 1
        cap_by_rank.append([rank, per_start["registered definition"],
                            per_start["only disconnected minimal holders"], per_start["at most one place per carrier at each knot"],
                            per_start["each carrier open under every single-knot fixing"],
                            per_start["at least one input can be replaced by an independent distinction"]])
    return {"totals": dict(totals), "heldout": dict(sample_totals), "source_bond_count_distribution": dict(distribution),
            "witnesses": witnesses, "by_source": cap_by_rank,
            "by_source_fields": ["archive rank", "registered bonds", "disconnected only", "one place per knot per carrier",
                                 "every feasible knot fixing keeps each reading open", "replaceable by independent input"]}


def alternatives(archive, ranks):
    totals = [Counter(), Counter()]
    witnesses = {}
    for rank in ranks:
        source = archive[rank]
        growth = advance(source)
        stages = (source, growth.supports) if growth.status == "funded" else (source,)
        for rd, supports in enumerate(stages):
            T = Truth(supports) if rd == 0 else None
            records = stage_records(supports, 4, carry_reader=T)
            counts = totals[rd]
            for C, (missing, certs, read) in records.items():
                H, first_mask = certs[0]
                counts["distinct carrier triples tested on whole stage"] += 1
                counts["same local image but read at a stage knot"] += missing == first_mask and read
                counts["different local and stage images"] += missing != first_mask
                counts["multiple local holders"] += len(certs) > 1
                different = len({mask for h, mask in certs}) > 1
                counts["multiple different local images"] += different
                if different:
                    key = f"round {rd} rank {rank} carriers {C}"
                    witnesses[key] = {"supports": supports, "carriers": C, "read_at_stage": read, "stage": labels(missing),
                                      "certificates": [[h, labels(m)] for h, m in certs]}
                if missing != first_mask or read:
                    counts["bond after replacing the first certificate by another"] += (
                        not read and any(m == missing for h, m in certs))
                    continue
                counts["accepted bonds"] += 1
                delta = len(set().union(*(set(supports[i]) for i in H))) - len(H)
                counts["count bound could fail for at least one of eight words, before reading image"] += delta > 3
                shape = "".join(str(len(c)) for c in C)
                if delta > 3:
                    counts["count bound could fail, carrier lengths " + shape] += 1
                counts["word positions tested for count bound"] += missing.bit_count()
                opposite = (1 << 8) - 1 - missing
                for w in range(8):
                    allowed = 3 + sum(len(c) == 3 and w & (4 >> i) != 0 for i, c in enumerate(C))
                    if allowed < delta:
                        counts["word positions violating bound if missing"] += 1
                        counts["such word positions actually present"] += bool(opposite & (1 << w))
    return {"round_0": dict(totals[0]), "round_1": dict(totals[1]), "differing_holder_images": witnesses}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("targeted", "population", "alternatives"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--ranks", nargs="+", type=int)
    parser.add_argument("--out", type=str)
    args = parser.parse_args()
    start = time.perf_counter()
    archive = inputs()
    raw = read_rows("census_nae_[0-9].jsonl")
    if args.kind == "targeted":
        data = targeted(archive, args.limit)
    elif args.kind == "population":
        ranks = list(range(len(archive)))[:args.limit] if args.ranks is None else args.ranks
        data = source_controls(archive, set(raw), ranks)
    else:
        ranks = sorted(raw)[:args.limit] if args.ranks is None else args.ranks
        data = alternatives(archive, ranks)
    data["elapsed_seconds"] = round(time.perf_counter()-start, 4)
    if args.out:
        (HERE / args.out).write_text(json.dumps(data, separators=(",", ":")) + "\n")
    print(json.dumps({k: v for k, v in data.items() if k in (
        "totals", "heldout", "round_0", "round_1", "elapsed_seconds")}, indent=1))


if __name__ == "__main__":
    main()

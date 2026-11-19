"""Blind exact-weight descents and exact-shape checks on fixed control rosters."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random

from control_hybrid import binomial_draw, binomial_transition, candidate_rows, classify, indices
from control_rosters import exact_truth, paired_start


PILOT_SEED = 202611190121
BATCHES = 32
BUDGETS = (64,256)


def seeded(label, batch):
    return Random(int.from_bytes(sha256(f"{PILOT_SEED}|{label}|{batch}".encode()).digest(), "big"))


def bits_of(items):
    return sum(1 << u for u in items)


def quantile(ordered, probability):
    rank = (len(ordered)-1)*probability
    i, remainder = divmod(rank.numerator, rank.denominator)
    if not remainder:
        return ordered[i]
    x = Fraction(remainder, rank.denominator)
    return (1-x)*ordered[i] + x*ordered[i+1]


def spread(series, truth):
    ordered = sorted(series)
    lo, hi = [quantile(ordered, q) for q in (Fraction(1,40), Fraction(39,40))]
    mean = sum(series, Fraction())/len(series)
    return {"truth": truth, "batch_count": len(series), "batch_means": [str(v) for v in series], "mean": str(mean),
            "signed_error": str(mean-truth), "signed_relative_error": str((mean-truth)/truth) if truth else None,
            "empirical_central_95": [str(lo),str(hi)], "fold": str(hi/lo) if lo > 0 else None,
            "zero_batch_means": ordered.count(0)}


def partnered_part(rows, cap=4):
    """Choose and certify a fixed deterministic part using only the candidate rows."""
    remaining = (1 << len(rows))-1
    pairs = []
    for _ in range(cap):
        choice = None
        for u in indices(remaining):
            vset = remaining & ~rows[u] & ~((1 << (u+1))-1)
            if vset:
                choice = (u,(vset & -vset).bit_length()-1)
                break
        if choice is None:
            break
        u,v = choice
        pairs.append(choice)
        remaining &= rows[u] & rows[v]
    assert len({u for pair in pairs for u in pair}) == 2*len(pairs)
    assert all(not (rows[u] & (1 << v)) for u,v in pairs)
    assert all(rows[u] & (1 << v) for a,b in combinations(pairs,2) for u in a for v in b)
    return pairs


class BlindDescent:
    """Unbiased integer inverse weights on a disjoint maximal-set partition."""

    def __init__(self, n, blocks):
        self.blocks = frozenset(blocks)
        self.rows = candidate_rows(n, blocks)
        self.root = (0, (1 << n)-1, 0)
        self.states = {}

    def expand(self, state):
        if state in self.states:
            return self.states[state]
        chosen, available, excluded = state
        must = [u for u in indices(available) if available & ~(self.rows[u] | (1 << u)) == 0]
        for u in must:
            chosen |= 1 << u
            available &= ~(1 << u)
            excluded &= self.rows[u]
        if not available:
            children = chosen if not excluded and chosen.bit_count() >= 3 and chosen not in self.blocks else 0
        elif any(available & ~self.rows[u] == 0 for u in indices(excluded)):
            children = 0
        else:
            pivot = max(indices(available | excluded), key=lambda u: (self.rows[u] & available).bit_count())
            branches = []
            for v in indices(available & ~self.rows[pivot]):
                one = 1 << v
                branches.append((chosen | one, available & self.rows[v], excluded & self.rows[v]))
                available ^= one
                excluded |= one
            children = tuple(branches)
        if len(self.states) < 16384:
            self.states[state] = children
        return children

    def draw(self, rng):
        state, weight = self.root, 1
        while isinstance(children := self.expand(state), tuple):
            weight *= len(children)
            state = children[rng.randrange(len(children))]
        return children, weight

    def literal_support(self, state_limit=250000):
        """Finite proof control for every sampling leaf and its second-moment term."""
        result = {}
        work = [(self.root,1)]
        checked = 0
        while work:
            state, weight = work.pop()
            checked += 1
            if checked > state_limit:
                return None
            children = self.expand(state)
            if isinstance(children, tuple):
                work.extend((child,weight*len(children)) for child in children)
            elif children:
                assert children not in result, "generic tree produced a group by multiple paths"
                result[children] = weight
        return result


def marks(group, blocks, part):
    size = group.bit_count()
    overlap = max(((group & b).bit_count() for b in blocks), default=0)
    return {"counts": 1, "size_at_least_four": int(size >= 4),
            "at_least_two_names_outside_every_block": int(size >= overlap+2),
            "meets_every_certified_partner_pair": int(bool(part) and all(group & p for p in part))}


def blind_trial(row):
    opens = tuple(row["loose"])
    blocks = tuple(bits_of(b) for b in row["blocks"])
    sampler = BlindDescent(len(opens), blocks)
    official = exact_truth(opens, blocks)
    for key in ("large_groups", "residual_pairs", "offshoots", "births"):
        assert row["truth"][key] == official[key]
    exact_groups = {bits_of(members) for members in official["literal_large"]}
    selected = partnered_part(sampler.rows)
    part = [bits_of(p) for p in selected]
    structural = {g: marks(g, blocks, part) for g in exact_groups}
    keys = tuple(marks(0, blocks, part))
    group_totals = {key: sum(m[key] for m in structural.values()) for key in keys}
    support = sampler.literal_support() if len(opens) <= 130 else None
    if support is not None:
        assert support.keys() == exact_groups
        # E[W^2] = sum of the inverse probabilities of accepted leaves.
        variance = sum(support.values()) - len(support)**2
        assert variance >= 0
        proof = {"all_positive_leaves": len(support), "true_single_draw_variance": variance}
    else:
        proof = None
    # No literal target or exact total is passed to draw() at any decision.
    batches = {k: {key: [] for key in keys} for k in BUDGETS}
    batch_zeros, weights_sum, max_weight = Counter(), 0, 0
    label = (row["name"], row["age"])
    for i in range(BATCHES):
        rng = seeded(label, i)
        running = Counter()
        for j in range(1, max(BUDGETS)+1):
            value, inverse = sampler.draw(rng)
            if value:
                assert value in structural
                traits = structural[value]
                for key in keys:
                    running[key] += inverse * traits[key]
                max_weight = max(max_weight, inverse)
                weights_sum += inverse
            else:
                batch_zeros[i] += 1
            if j in BUDGETS:
                for key in keys:
                    batches[j][key].append(Fraction(running[key],j))
    return {"name": row["name"], "age": row["age"], "N": len(opens), "blocks_sha256": row["blocks_sha256"],
            "target": "unheld maximal groups of arity at least three", "theoretical_bias": 0,
            "old_partnered_part": selected, "independent_exact_target": group_totals,
            "exact_pair_and_offshoot_correction_for_context": [official["residual_pairs"],official["offshoots"]],
            "exact_tree_audit": proof,
            "zero_draws_through_256": sum(batch_zeros.values()),
            "largest_weight_share_of_draw_sum": str(Fraction(max_weight,weights_sum)) if weights_sum else None,
            "observations": {str(k): {key: spread(data,group_totals[key]) for key,data in item.items()}
                             for k,item in batches.items()}}


def hybrid_trial(row):
    opens = tuple(row["loose"])
    blocks = tuple(bits_of(b) for b in row["blocks"])
    table = classify(opens,blocks)
    assert table is not None and table.births
    if "truth" in row:
        given = row["truth"]
        assert (table.large_groups,table.residual_pairs,table.offshoots,table.births) == (
            given["large_groups"],given["residual_pairs"],given["offshoots"],given["births"])
    elif "known_births" in row:
        assert table.births == row["known_births"]
    if table.births <= 5000:
        known = exact_truth(opens, blocks)
        inverses = [table.at(j,"births") for j in range(table.births)]
        pairs, large = ({d.parents for d in inverses if d.kind == kind} for kind in ("pair","large"))
        assert pairs == set(known["literal_pairs"]) and large == set(known["literal_large"])
        assert Counter(d.parents[0] for d in inverses if d.kind == "offshoot") == {
            u:d for u,d in enumerate(known["offshoot_by_parent"]) if d}
        assert all(d.inverse_probability == table.births for d in inverses)
    marker_truth = table.loose[0]  # total births consume all old loose distinctions
    counts = Counter()
    label = (row["name"],row["age"],"structural_uniform")
    batches = {k: [] for k in BUDGETS}
    for i in range(BATCHES):
        rng = seeded(label,i)
        partial = 0
        for j in range(1,max(BUDGETS)+1):
            d = table.sample(rng,"births")
            counts[d.kind] += 1
            assert d.inverse_probability == table.births
            assert len(set(d.parents)) == len(d.parents)
            partial += d.inverse_probability * (0 in d.parents)
            if j in BUDGETS:
                batches[j].append(Fraction(partial,j))
    return {"name": row["name"], "age": row["age"], "blocks_sha256": row["blocks_sha256"],
            "recognized": table.kind, "held_transversals": len(table.held), "roster_size": len(opens),
            "exact_large_count": table.large_groups, "exact_pair_count": table.residual_pairs,
            "drawn_kind_counts": dict(counts), "constant_inverse_probability": table.births,
            "count_empirical_spread": "1 by structural uniform design",
            "point_zero_marked_birth_total": {str(k):spread(v,marker_truth) for k,v in batches.items()}}


def edge_cases():
    # The two held words share exactly the same choice on pairs 0 and 1.
    # Their compatible pair has no unheld completion and becomes residual.
    opens, pairs = paired_start(3)
    held = [(1 << 0) | (1 << 2) | (1 << other) for other in (4,5)]
    table = classify(opens, (*pairs,*held))
    assert table is not None
    assert table.residual == ((0,2),) and table.large_groups == 6
    assert table.births == exact_truth(opens,(*pairs,*held))["births"]
    invalid = classify(opens, pairs[1:])
    assert invalid is None
    # The recognizer and the literal group support commute with arbitrary names.
    permutation = (5,2,3,4,1,0)
    recoded_blocks = tuple(bits_of(permutation[u] for u in indices(b)) for b in (*pairs,*held))
    recoded = classify(opens, recoded_blocks)
    assert recoded is not None and recoded.births == table.births
    actual = {recoded.at(j,"groups").parents for j in range(recoded.large_groups+recoded.residual_pairs)}
    expected = {tuple(sorted(permutation[u] for u in table.at(j,"groups").parents))
                for j in range(table.large_groups+table.residual_pairs)}
    assert actual == expected
    all_held = [bits_of((a,b,c)) for a in (0,1) for b in (2,3) for c in (4,5)]
    no_large = classify(opens, all_held)
    assert no_large is not None and no_large.large_groups == 0 and no_large.residual_pairs == no_large.births == 12
    ring = classify((1,1),(3,))
    assert ring is not None and ring.closes_on_next_birth and ring.births == 1
    closed = classify((),())
    assert closed is not None and closed.births == 0
    try:
        closed.sample(Random(1),"births")
    except ValueError:
        pass
    else:
        raise AssertionError("a terminal stage has no sampleable birth")
    # Uniform tail samples are backed by their definite binomial transitions.
    tail = []
    for n, positions in [(9,range(1,9)),(781,(1,2,3,780))]:
        for k in positions:
            forecast = binomial_transition(n,k)
            test = binomial_draw(n,k,seeded((n,k),0))
            assert test.inverse_probability == forecast["births"] and len(test.parents) == forecast["parents"]
            assert all(0 <= v < forecast["current_population"] for v in test.parents)
            literal = n == 9
            if literal:
                parents_id = lambda s: sum(comb(v,i) for i,v in enumerate(s,1))
                points = list(combinations(range(n), k))
                blocks = tuple(bits_of(parents_id(s) for s in points if set(lower).issubset(s))
                               for lower in combinations(range(n), k-1))
                actual_truth = exact_truth((n-k,)*len(points),blocks)
                actual = set(actual_truth["literal_large"]+actual_truth["literal_pairs"])
                expected = {tuple(sorted(parents_id(seq[:j]+seq[j+1:]) for j in range(len(seq))))
                            for seq in combinations(range(n), k+1)}
                assert actual == expected and actual_truth["births"] == forecast["births"]
            tail.append({"base": n, "source_subset_size": k, "literal_group_truth":literal, **forecast})
    return {"forced_residual_pair": [0,2], "invalid_pairing_rejected": True, "renaming_preserved_support": True,
            "all_transversals_held_residual_pairs": no_large.residual_pairs,
            "closing_births": ring.births,
            "post_closure_births": closed.births, "binomial_transitions": tail}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("rosters", type=Path)
    cli.add_argument("output", type=Path)
    cli.add_argument("--only", choices=("all","hybrid","blind"), default="all")
    args = cli.parse_args()
    records = json.loads(args.rosters.read_text())
    result = {"pilot_seed": PILOT_SEED, "batches": BATCHES, "draw_budgets": BUDGETS, "edge_cases": edge_cases()}
    if args.only in {"all","hybrid"}:
        hybrids = [r for r in records if r["name"].startswith("partner-") or r.get("recognition") == "single_block"]
        result["structural_exact_uniform"] = [hybrid_trial(r) for r in hybrids]
    if args.only in {"all","blind"}:
        blind = [r for r in records if r["name"].startswith("start-") and "truth" in r]
        result["fixed_blind_baseline"] = [blind_trial(r) for r in blind]
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

"""Exact test of every third carrier with the two carriers of an upper reading fixed."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
import gzip
from itertools import combinations
import json
from math import comb
from operator import and_, or_
from pathlib import Path
from random import Random
from time import perf_counter

import numpy as np
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
SAMPLE_COUNT = 2048
BASE_SEED = 506177
PAIR_MASKS = [
    sum(1 << w for w in range(8) if w & selected == value)
    for selected in (6, 5, 3)
    for value in range(8)
    if value & ~selected == 0
]


def paired_carriers(supports, chain):
    laws = [set(supports[k]) for k in chain]
    shared = [next(iter(a & b)) for a, b in zip(laws, laws[1:])]
    assert all(len(a & b) == 1 for a, b in zip(laws, laws[1:]))
    assert all(laws[i].isdisjoint(laws[j]) for i, j in combinations(range(8), 2) if j != i + 1)
    own = [law.difference(shared) for law in laws]
    groups = [
        (own[1] | {shared[1]} | own[2], own[5] | {shared[5]} | own[6]),
        (own[0] | {shared[4]}, own[7] | {shared[2]}),
        (own[3] | {shared[3]} | own[4], {shared[0], shared[6]}),
    ]
    return [tuple(sorted(tuple(sorted(carrier)) for carrier in group)) for group in groups]


def stage_clauses(supports, offset=0):
    for law in supports:
        row = [x + offset + 1 for x in law]
        yield row
        yield [-v for v in row]


def witness_columns(supports, model, count, seed):
    """Return verified allowed source states packed one bit per state in each raw column."""
    full = (1 << count) - 1
    rng = Random(seed)
    n = max(max(law) for law in supports) + 1
    columns = [full if v > 0 else 0 for v in model[:n]]
    others = [[] for _ in range(n)]
    for law in supports:
        for x in law:
            others[x].append(tuple(z for z in law if z != x))
    order = list(range(n))
    for _ in range(12):
        rng.shuffle(order)
        for x in order:
            force_zero = force_one = 0
            for group in others[x]:
                all_one = full
                any_one = 0
                for z in group:
                    all_one &= columns[z]
                    any_one |= columns[z]
                force_zero |= all_one
                force_one |= full ^ any_one
            assert not force_zero & force_one
            columns[x] = (rng.getrandbits(count) | force_one) & ~force_zero
    for law in supports:
        assert not reduce(and_, (columns[x] for x in law))
        assert reduce(or_, (columns[x] for x in law)) == full
    return columns


def agreement(columns, carrier, full):
    a = columns[carrier[0]]
    differences = reduce(or_, (a ^ columns[b] for b in carrier[1:]))
    return full ^ differences


class Source:
    def __init__(self, supports):
        self.supports = [tuple(s) for s in supports]
        self.n = max(max(s) for s in self.supports) + 1
        assert set(range(self.n)) == set().union(*map(set, self.supports))
        self.solver = Solver(bootstrap_with=stage_clauses(self.supports))
        assert self.solver.solve()
        self.model = self.solver.get_model()
        self.signals = {}
        self.nonlocal_cache = {}
        self.contained = {
            tuple(sorted(c)) for law in self.supports for size in (2, 3) for c in combinations(law, size)
        }

    def signal(self, carrier):
        if carrier in self.signals:
            return self.signals[carrier]
        a = self.n + len(self.signals) + 1
        raw = [x + 1 for x in carrier]
        for v in raw[1:]:
            self.solver.add_clause([-a, -raw[0], v])
            self.solver.add_clause([-a, raw[0], -v])
        self.solver.add_clause([a] + raw)
        self.solver.add_clause([a] + [-v for v in raw])
        self.signals[carrier] = a
        return a

    def possible(self, assumptions, carrier, equal):
        # Global complementation fixes the first raw bit at zero.
        if equal:
            return self.solver.solve(assumptions=assumptions + [-(v + 1) for v in carrier])
        first = -(carrier[0] + 1)
        return any(self.solver.solve(assumptions=assumptions + [first, z + 1]) for z in carrier[1:])

    def unread_at_every_knot(self, carrier):
        if carrier in self.contained:
            return False
        if carrier in self.nonlocal_cache:
            return self.nonlocal_cache[carrier]
        n = self.n
        with Solver(bootstrap_with=stage_clauses(self.supports)) as twin:
            twin.append_formula(stage_clauses(self.supports, n))
            for x in carrier:
                twin.add_clause([-(x + 1)])
            second = [n + x + 1 for x in carrier]
            twin.add_clause(second)
            twin.add_clause([-v for v in second])
            for x in range(n):
                p, q, selector = x + 1, n + x + 1, 2 * n + x + 1
                twin.add_clause([-selector, -p, q])
                twin.add_clause([-selector, p, -q])
            result = all(twin.solve(assumptions=[2 * n + x + 1 for x in law]) for law in self.supports)
        self.nonlocal_cache[carrier] = result
        return result


class ThirdIndices:
    """All pairs and triples, ordered by largest index so each initial segment is reusable."""

    def __init__(self, n):
        self.tables = {}
        for size in (2, 3):
            table = np.empty((size, comb(n, size)), dtype=np.int16)
            for last in range(size - 1, n):
                begin, end = comb(last, size), comb(last + 1, size)
                if size == 2:
                    table[0, begin:end] = np.arange(last)
                else:
                    table[:2, begin:end] = np.triu_indices(last, 1)
                table[-1, begin:end] = last
            self.tables[size] = table

    def for_size(self, n, size):
        return self.tables[size][:, :comb(n, size)]


def state_matrix(columns, count):
    """The same legal rows in an array, for choosing 64 states at each fixed pair value."""
    width = (count + 7) // 8
    rows = b''.join(value.to_bytes(width, "little") for value in columns)
    raw = np.frombuffer(rows, dtype=np.uint8).reshape(len(columns), width)
    return np.unpackbits(raw, bitorder="little", axis=1)[:, :count]


def first_word(states, condition, available):
    width = (states.shape[1] + 7) // 8
    mask = np.frombuffer(condition.to_bytes(width, 'little'), dtype=np.uint8)
    subset = np.flatnonzero(np.unpackbits(mask, bitorder="little"))[:64]
    assert len(subset)
    chosen = states[np.ix_(available, subset)]
    encoded = np.zeros((len(available), 8), dtype=np.uint8)
    packed = np.packbits(chosen, bitorder="little", axis=1)
    encoded[:, :packed.shape[1]] = packed
    values = encoded.view("<u8").ravel()
    full = np.uint64((1 << len(subset)) - 1)
    return full ^ np.bitwise_xor.outer(values, values), full


def examine_pair(source, pair, columns, states, count, choice):
    a, b = pair
    available = sorted(set(range(source.n)).difference(a, b))
    full = (1 << count) - 1
    x, y = agreement(columns, a, full), agreement(columns, b, full)
    sig_x, sig_y = source.signal(a), source.signal(b)
    missing = defaultdict(int)
    counts = Counter()
    counts["possible_third_carriers"] = sum(comb(len(available), size) for size in (2, 3))
    counts["third_carriers_contained_at_a_knot"] = sum(set(z).isdisjoint(a + b) for z in source.contained)
    for pattern in range(4):
        condition = (x if pattern & 2 else full ^ x) & (y if pattern & 1 else full ^ y)
        assumptions = [sig_x if pattern & 2 else -sig_x, sig_y if pattern & 1 else -sig_y]
        first, first_full = first_word(states, condition, available) if condition else (None, None)
        for size in (2, 3):
            indices = choice.for_size(len(available), size)
            if condition:
                eq = first[indices[0], indices[1]]
                if size == 3:
                    eq &= first[indices[0], indices[2]]
            for target in (0, 1):
                if condition:
                    unresolved = np.flatnonzero(eq == (0 if target else first_full))
                else:
                    unresolved = range(indices.shape[1])
                counts["missing_in_first_witnesses_including_contained"] += len(unresolved)
                for pos in unresolved:
                    z = tuple(available[i] for i in indices[:, pos])
                    if z in source.contained:
                        continue
                    z_values = agreement(columns, z, full)
                    if condition & (z_values if target else full ^ z_values):
                        continue
                    counts["third_word_exact_queries"] += 1
                    if not source.possible(assumptions, z, target):
                        missing[z] |= 1 << (pattern * 2 + target)
    result = []
    for z, absent in sorted(missing.items()):
        present = 255 ^ absent
        if not all(present & mask for mask in PAIR_MASKS):
            counts["proper_relations_with_a_nonfree_pair"] += 1
        elif all(source.unread_at_every_knot(c) for c in (a, b, z)):
            result.append({"third": z, "missing_words": [format(i, "03b") for i in range(8) if absent & (1 << i)]})
        else:
            counts["proper_pairwise_free_with_a_local_reading"] += 1
    counts["proper_pairwise_free_bonds_with_all_readings_nonlocal"] = len(result)
    return counts, result


def direct_control(source, pair):
    n = source.n
    states = np.arange(1 << n, dtype=np.uint32)
    for support in source.supports:
        mask = sum(1 << x for x in support)
        states = states[((states & mask) != 0) & ((states & mask) != mask)]
    columns = [int.from_bytes(np.packbits((states >> x) & 1, bitorder="little"), "little") for x in range(n)]
    full = (1 << len(states)) - 1
    local_cells = []
    for support in source.supports:
        mask = sum(1 << x for x in support)
        values = states & mask
        local_cells.append([int.from_bytes(np.packbits(values == v, bitorder="little"), "little") for v in np.unique(values)])
    def unread(value):
        return all(any(cell & value and cell & (full ^ value) for cell in cells) for cells in local_cells)
    a, b = pair
    x, y = agreement(columns, a, full), agreement(columns, b, full)
    assert unread(x) and unread(y)
    conditional = [(x if i & 2 else full ^ x) & (y if i & 1 else full ^ y) for i in range(4)]
    found = []
    remaining = sorted(set(range(n)).difference(a, b))
    for size in (2, 3):
        for carrier in combinations(remaining, size):
            z = agreement(columns, carrier, full)
            present = sum(1 << i for i in range(8) if conditional[i // 2] & (z if i & 1 else full ^ z))
            if present != 255 and all(present & mask for mask in PAIR_MASKS) and unread(z):
                found.append({"third": carrier, "missing_words": [format(i, "03b") for i in range(8) if not present & (1 << i)]})
    return sorted(found, key=lambda rec: rec["third"]), len(states)


def controls(choice):
    law = [(2*i, 2*i + 1, 2*i + 2) for i in range(8)]
    source = Source(law)
    columns = witness_columns(law, source.model, SAMPLE_COUNT, BASE_SEED)
    states = state_matrix(columns, SAMPLE_COUNT)
    pairs = paired_carriers(law, range(8))
    assert pairs == paired_carriers(law, reversed(range(8)))
    positive = (pairs[0][0], pairs[1][0])
    result = []
    for label, pair in [(f"upper pair {i + 1}", p) for i, p in enumerate(pairs)] + [("members of one defining lower clause", positive)]:
        counts, found = examine_pair(source, pair, columns, states, SAMPLE_COUNT, choice)
        direct, allowed = direct_control(source, pair)
        assert found == direct, (label, found, direct)
        assert bool(found) == (pair == positive)
        result.append({"case": label, "pair": pair, "direct_allowed_states": allowed, "agrees_with_full_truth_table": True,
                       "counts": counts, "bonds": found})
    source.solver.delete()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start = perf_counter()
    with gzip.open(HERE / "stages.jsonl.gz", "rt") as f:
        stages = [row for line in f if (row := json.loads(line))["checked_chains"]]
    largest = max(1 + max(max(law) for law in row["supports"]) for row in stages)
    choice = ThirdIndices(largest)
    checks = controls(choice)
    if args.pilot:
        keys = {(0, 3), (90, 4), (1278, 6)}
        stages = [row for row in stages if (row["start"], row["round"]) in keys]
    mode = "pilot" if args.pilot else "all"
    counts = Counter()
    distinct_counts = Counter()
    rows_written = 0
    stage_times = []
    hits = []
    affected_starts = set()
    affected_stages = 0
    chain_totals = Counter()
    round_totals = defaultdict(Counter)
    positive_starts = set()
    first_positive = {}
    with (HERE / f"other_bonds_paired_{mode}.jsonl.gz").open("wb") as dest, gzip.GzipFile(fileobj=dest, mode="wb", mtime=0, filename="") as out:
        for row in stages:
            begin = perf_counter()
            key = (row["start"], row["round"])
            source = Source(row["supports"])
            columns = witness_columns(source.supports, source.model, SAMPLE_COUNT, BASE_SEED + 11 * key[0] + key[1])
            states = state_matrix(columns, SAMPLE_COUNT)
            roles = defaultdict(list)
            for i, chain in enumerate(row["checked_chains"]):
                pairs = paired_carriers(source.supports, chain)
                assert pairs == paired_carriers(source.supports, reversed(chain))
                for j, pair in enumerate(pairs):
                    roles[pair].append((i, j))
            stage_records = []
            affected_chains = set()
            for pair, slots in roles.items():
                result, bonds = examine_pair(source, pair, columns, states, SAMPLE_COUNT, choice)
                distinct_counts.update(result)
                for _ in slots:
                    counts.update(result)
                if bonds:
                    hits.append({"stage": key, "pair": pair, "chain_and_pair_slots": slots, "bonds": bonds})
                    affected_chains.update(i for i, j in slots)
                stage_records.append({"pair": pair, "chain_and_pair_slots": slots, "counts": result, "bonds": bonds})
                rows_written += 1
            source.solver.delete()
            affected_stages += bool(affected_chains)
            if affected_chains:
                affected_starts.add(key[0])
            stage_counts = Counter()
            for i, archive in enumerate(row["recorded"]["mapped"]):
                passed_frozen = archive["a step"]
                passed_with_laws = passed_frozen and archive["every chain law needed"]
                stage_counts["mapped_chains"] += 1
                stage_counts["chains_with_determining_fixed_pair"] += i in affected_chains
                stage_counts["frozen_positives_with_determining_fixed_pair"] += passed_frozen and i in affected_chains
                stage_counts["frozen_positives_needing_all_laws_with_determining_fixed_pair"] += passed_with_laws and i in affected_chains
                stage_counts["frozen_positives_needing_all_laws_surviving_fixed_pair_test"] += passed_with_laws and i not in affected_chains
            if stage_counts["frozen_positives_needing_all_laws_surviving_fixed_pair_test"]:
                stage_counts["stages_with_at_least_one_surviving_checked_chain"] += 1
                positive_starts.add(key[0])
                first_positive[key[0]] = min(first_positive.get(key[0], key[1]), key[1])
            chain_totals.update(stage_counts)
            round_totals[key[1]].update(stage_counts)
            out.write((json.dumps({"start": key[0], "round": key[1], "fixed_pairs": stage_records}, separators=(",", ":")) + "\n").encode())
            stage_times.append(perf_counter() - begin)
    summary = {
        "mode": mode, "witnesses_per_stage_before_exact_completion": SAMPLE_COUNT, "seed": BASE_SEED,
        "stages": len(stages), "chains": sum(len(row["checked_chains"]) for row in stages),
        "unique_pairs_within_stages": rows_written, "counts_by_chain_and_pair": counts,
        "counts_by_unique_pair_within_stage": distinct_counts, "genuine_bond_cases": hits,
        "stages_with_determining_fixed_pair": affected_stages, "starts_with_determining_fixed_pair": len(affected_starts),
        "chain_and_stage_counts": chain_totals, "chain_and_stage_counts_by_round": dict(sorted(round_totals.items())),
        "starts_with_any_survivor": len(positive_starts), "first_round_with_survivor": dict(sorted(Counter(first_positive.values()).items())),
        "controls": checks, "stage_seconds_total": round(sum(stage_times), 3),
        "stage_seconds_max": round(max(stage_times), 3), "seconds_including_controls": round(perf_counter() - start, 3),
    }
    if args.pilot:
        summary["timed_stages"] = [(row["start"], row["round"], round(t, 3)) for row, t in zip(stages, stage_times)]
    (HERE / f"other_bonds_paired_{mode}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("mode", "stages", "chains", "counts_by_chain_and_pair",
                                                    "unique_pairs_within_stages", "stage_seconds_total")}))


if __name__ == "__main__":
    main()

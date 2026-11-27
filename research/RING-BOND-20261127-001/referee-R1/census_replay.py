"""Enumerate not-all-equal holder certificates and independently check their stage images."""

import argparse
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import sys
import time

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance, supports_of


def inputs():
    archive = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    return tuple(supports_of(record) for record in archive)


def order(carrier):
    return len(carrier), carrier


@cache
def bits(dimensions):
    """All assignments with the first distinction fixed, one bit per assignment."""
    count = 1 << (dimensions - 1)
    full = (1 << count) - 1
    columns = [0]
    for k in range(dimensions - 1):
        run = 1 << k
        unit = (1 << run) - 1
        # The low run is zero; the next run is one, alternating.
        columns.append((full // ((1 << (2 * run)) - 1)) * (unit << run))
    return full, tuple(columns)


class Truth:
    def __init__(self, supports):
        self.names = sorted(set().union(*map(set, supports)))
        self.full, columns = bits(len(self.names))
        self.columns = dict(zip(self.names, columns))
        self.yes = {}
        self.supports = tuple(map(tuple, supports))
        self.laws = tuple(self.full ^ self.agreement(C) for C in supports)
        self.allowed = self.full
        for law in self.laws:
            self.allowed &= law
        self.deleted = []
        for i in range(len(supports)):
            allowed = self.full
            for j, law in enumerate(self.laws):
                if j != i:
                    allowed &= law
            self.deleted.append(allowed)
        self.fixings = tuple(self._fixings(C) for C in supports)
        self.profiles = {}

    def agreement(self, C):
        if C not in self.yes:
            all_one, all_zero = self.full, self.full
            for x in C:
                all_one &= self.columns[x]
                all_zero &= self.full ^ self.columns[x]
            self.yes[C] = all_one | all_zero
        return self.yes[C]

    def _fixings(self, C):
        cells = [self.allowed]
        for x in C[1:]:
            opposed = self.columns[x] ^ self.columns[C[0]]
            cells = [part for c in cells for part in (c & opposed, c & ~opposed) if part]
        return tuple(cells)

    def profile(self, C):
        """Total single-knot functions and feasible fixings forcing the reading."""
        if C not in self.profiles:
            yes = self.agreement(C)
            counts = tuple(sum(not (p & yes and p & ~yes) for p in F) for F in self.fixings)
            self.profiles[C] = (any(n == len(F) for n, F in zip(counts, self.fixings)), sum(counts))
        return self.profiles[C]

    def cells(self, carriers):
        cells = [self.full]
        for C in carriers:
            yes = self.agreement(C)
            cells = [cell for previous in cells for cell in (previous & ~yes, previous & yes)]
        return cells

    def image(self, carriers, allowed=None):
        allowed = self.allowed if allowed is None else allowed
        return sum(1 << i for i, c in enumerate(self.cells(carriers)) if not c & allowed)


VALID = tuple(0 < m < 255 and all(
    any(not m & (1 << word) for word in range(8) if (word & ~bit) == (value & ~bit))
    for bit in (1, 2, 4) for value in range(8)
) for m in range(256))


def connected(supports):
    seen = {0}
    while True:
        covered = set().union(*(set(supports[i]) for i in seen))
        reached = {i for i, C in enumerate(supports) if covered.intersection(C)}
        if reached == seen:
            return len(reached) == len(supports)
        seen = reached


@cache
def canonical_order(signature, size):
    patterns = tuple(mask for mask, count in signature for _ in range(count))
    permutation_rows = []
    for perm in permutations(range(size)):
        new_masks = tuple(sorted(sum(1 << new for new, old in enumerate(perm) if mask & (1 << old))
                                 for mask in patterns))
        permutation_rows.append((new_masks, perm))
    shape, perm = min(permutation_rows)
    translation = {mask: sum(1 << new for new, old in enumerate(perm) if mask & (1 << old))
                   for mask, count in signature}
    return shape, translation


def holder_type(supports):
    incident = {}
    for i, C in enumerate(supports):
        for x in C:
            incident[x] = incident.get(x, 0) | 1 << i
    size = len(supports)
    if len(incident) < 6 or sum(m.bit_count() == 1 for m in incident.values()) > 9:
        return None
    signature = tuple(sorted(Counter(incident.values()).items()))
    shape, translation = canonical_order(signature, size)
    to_stage = tuple(sorted(incident, key=lambda x: (translation[incident[x]], x)))
    return shape, size, to_stage


@cache
def enumerate_type(shape, size):
    """Search all three-reading candidates using every law of these holders."""
    names = tuple(range(len(shape)))
    supports = tuple(tuple(x for x, mask in enumerate(shape) if mask & (1 << k)) for k in range(size))
    T = Truth(supports)
    candidates = []
    local = tuple(C for v in (2, 3) for C in combinations(names, v)
                  if not any(set(C) <= set(H) for H in supports))
    carriers = [C for C in local if not T.profile(C)[0]]
    masks = [sum(1 << x for x in C) for C in carriers]
    yes = [T.agreement(C) for C in carriers]
    local1 = [s & T.allowed for s in yes]
    local0 = [T.allowed ^ s for s in local1]
    loose = sum(1 << x for x, incidence in enumerate(shape) if incidence.bit_count() == 1)
    names_mask = (1 << len(names)) - 1
    by_mask = {v: i for i, v in enumerate(masks)}
    thirds = {}
    for i, (a, ma) in enumerate(zip(carriers, masks)):
        for j in range(i + 1, len(carriers)):
            mb = masks[j]
            if ma & mb:
                continue
            used = ma | mb
            gap = loose & ~used
            if gap.bit_count() > 3:
                continue
            if used not in thirds:
                available = tuple(x for x in names if (1 << x) & (names_mask ^ used) & ~gap)
                options = []
                for length in (2, 3):
                    extra = length - gap.bit_count()
                    if extra >= 0:
                        for xs in combinations(available, extra):
                            k = by_mask.get(gap | sum(1 << x for x in xs))
                            if k is not None:
                                options.append(k)
                thirds[used] = options
            parts = (local0[i] & local0[j], local0[i] & local1[j],
                     local1[i] & local0[j], local1[i] & local1[j])
            if not all(parts):
                continue
            for k in thirds[used]:
                if k <= j:
                    continue
                pk, nk = local1[k], local0[k]
                p0, p1, p2, p3 = parts
                # The common outcome is that all eight words occur.
                if p0 & pk and p1 & pk and p2 & pk and p3 & pk and p0 & nk and p1 & nk and p2 & nk and p3 & nk:
                    continue
                missing = sum((1 << (2*h)) * (not p & nk) + (2 << (2*h)) * (not p & pk)
                              for h, p in enumerate(parts))
                if not VALID[missing]:
                    continue
                C = (a, carriers[j], carriers[k])
                cells = T.cells(C)
                excluded = 0
                for h, cell in enumerate(cells):
                    if missing & (1 << h):
                        excluded |= cell
                if all(allowed & excluded for allowed in T.deleted):
                    candidates.append((C, missing))
    return candidates


@cache
def move_words(missing, permutation):
    result = 0
    for w in range(8):
        if missing & (1 << w):
            new = sum(((w >> (2-i)) & 1) << (2-j) for j, i in enumerate(permutation))
            result |= 1 << new
    return result


def local_candidates(supports, cap, *, connected_only=True):
    """Yield (carriers, holder, missing-mask) per certificate, including alternative holders."""
    for size in range(2, min(len(supports), cap) + 1):
        for H in combinations(range(len(supports)), size):
            subset = tuple(supports[i] for i in H)
            if connected_only and not connected(subset):
                continue
            spec = holder_type(subset)
            if spec is None:
                continue
            shape, n, to_stage = spec
            for canon, missing in enumerate_type(shape, n):
                mapped = tuple(tuple(sorted(to_stage[x] for x in C)) for C in canon)
                perm = tuple(sorted(range(3), key=lambda i: order(mapped[i])))
                yield tuple(mapped[i] for i in perm), H, move_words(missing, perm)


class StageReader:
    """Exact restriction queries on two independently constrained copies of the stage."""
    def __init__(self, supports):
        self.supports = supports
        self.solver = Solver()
        self.version = 0
        self.names = sorted(set().union(*map(set, supports)))
        self.selectors = tuple(self.var() for _ in supports)
        self.copies = []
        for _ in range(2):
            xs = {x: self.var() for x in self.names}
            self.copies.append(xs)
            for e, C in zip(self.selectors, supports):
                self.solver.add_clause([-e] + [xs[x] for x in C])
                self.solver.add_clause([-e] + [-xs[x] for x in C])
        self.equal_guards = []
        for C in supports:
            guard = self.var()
            self.equal_guards.append(guard)
            for x in C:
                a, b = (ys[x] for ys in self.copies)
                self.solver.add_clause([-guard, a, -b])
                self.solver.add_clause([-guard, -a, b])
        self.views = {}
        self.read_at = {}

    def var(self):
        self.version += 1
        return self.version

    def view(self, C):
        if C not in self.views:
            views = []
            for xs in self.copies:
                r = self.var()
                views.append(r)
                for word in product((0, 1), repeat=len(C)):
                    clause = [-xs[x] if xval else xs[x] for x, xval in zip(C, word)]
                    clause.append(r if all(b == word[0] for b in word) else -r)
                    self.solver.add_clause(clause)
            self.views[C] = tuple(views)
        return self.views[C]

    def reads(self, C):
        if C not in self.read_at:
            a, b = self.view(C)
            self.read_at[C] = any(not self.solver.solve(assumptions=[*self.selectors, guard, a, -b])
                                  for guard in self.equal_guards)
        return self.read_at[C]

    def image(self, carriers):
        views = [self.view(C)[0] for C in carriers]
        return sum(1 << w for w in range(8) if not self.solver.solve(assumptions=[
            *self.selectors, *(v if w & (4 >> i) else -v for i, v in enumerate(views))]))

    def close(self):
        self.solver.delete()


def stage_records(supports, cap, *, connected_only=True, carry_reader=None):
    """Map each carrier triple to (stage missing-mask, certificates, readable-on-stage)."""
    found = defaultdict(list)
    for C, H, missing in local_candidates(supports, cap, connected_only=connected_only):
        found[C].append((H, missing))
    if not found:
        return {}
    truth = carry_reader
    sat = None if truth is not None else StageReader(supports)
    result = {}
    for C, certificates in found.items():
        if truth is None:
            missing = sat.image(C)
            readable = any(sat.reads(c) for c in C)
        else:
            missing = truth.image(C)
            readable = any(truth.profile(c)[0] for c in C)
        result[C] = (missing, certificates, readable)
    if sat is not None:
        sat.close()
    return result


def labels(mask):
    return [format(w, "03b") for w in range(8) if mask & 1 << w]


def summaries(supports, records, born):
    good = {}
    shapes, holders, missing_sizes, shared = Counter(), Counter(), Counter(), Counter()
    auxiliary = Counter()
    agree = count_fails = new = 0
    for C, (missing, certs, read) in records.items():
        H, chosen = certs[0]
        alternative = [(hh, m) for hh, m in certs if m == missing]
        if len(certs) > 1:
            auxiliary["carrier triples with multiple local holders"] += 1
            auxiliary["multiple holders with different images"] += len({m for hh, m in certs}) > 1
        if missing != chosen or read:
            if alternative and not read:
                auxiliary["valid only after changing chosen holders"] += 1
            continue
        good[C] = (H, missing)
        shape = "".join(str(len(c)) for c in C)
        shapes[f"{shape} missing {missing.bit_count()}"] += 1
        missing_sizes[str(missing.bit_count())] += 1
        holders[str(len(H))] += 1
        new += bool(born and max(H) >= born)
        agree += bool(missing & (1 << 7))
        shared.update(C)
        d = len(set().union(*(set(supports[i]) for i in H)))
        for w in range(8):
            if missing & (1 << w):
                # Each pair gives one, every triple two (either two merges, or one added law).
                allowance = sum(len(c)-1 if w & (4 >> i) else 1 for i, c in enumerate(C))
                if d > len(H) + allowance:
                    count_fails += 1
                    break
    base = {"distinctions": len(set().union(*map(set, supports))), "knots": len(supports),
            "bonds": len(good), "by shape and missing count": dict(shapes),
            "all agree missing": agree, "bound fails": count_fails,
            "with a birth among the holders": new, "missing counts": dict(missing_sizes),
            "holder sizes": dict(holders), "readings in two or more bonds": sum(n >= 2 for n in shared.values()),
            "found on the holders but not a bond of the stage": len(records) - len(good)}
    return good, base, auxiliary


def extra_checks(supports, good, records, T):
    counts = Counter()
    witnesses = {}
    for C, (H, missing) in good.items():
        cells = T.cells(C)
        absent = [part for i, part in enumerate(cells) if missing & 1 << i]
        essential = [i for i, allow in enumerate(T.deleted) if any(part & allow for part in absent)]
        strict_place = all(len(set(c).intersection(h)) <= 1 for c in C for h in supports)
        each_open = not any(T.profile(c)[1] for c in C)
        all_fixings = all(all((cell & f) or not (cell & T.allowed) for cell in cells)
                          for F in T.fixings for f in F)
        reductions = []
        equivalent = []
        for i, c in enumerate(C):
            if len(c) != 3:
                continue
            for small in combinations(c, 2):
                altered = tuple(small if j == i else cc for j, cc in enumerate(C))
                if not ((T.agreement(c) ^ T.agreement(small)) & T.allowed):
                    equivalent.append((i, small))
                if T.image(altered) == missing:
                    reductions.append((i, small, T.profile(small)[0]))
        weak_pad = bool(reductions)
        pad = any(not read for i, s, read in reductions)
        flag = {
            "at most one place per carrier at each knot": strict_place,
            "every carrier stays open under every single-knot fixing": each_open,
            "every single-knot fixing keeps the full joint image": all_fixings,
            "same reading after dropping a carrier place": bool(equivalent),
            "same relation after dropping a carrier place": weak_pad,
            "same bond after dropping a carrier place": pad,
            "no single-place deletion keeps a bond with the same image": not pad,
            "strict places and no single-place deletion keeps same bond": strict_place and not pad,
            "all chosen holder laws essential on whole stage": tuple(essential) == H,
            "each holder deletion restores all eight on whole stage": all(
                all(part & T.deleted[i] for part in absent) for i in H),
            "every law of stage essential": len(essential) == len(supports),
            "valid certificates for same stage image with multiple holders": sum(m == missing for h, m in records[C][1]) > 1,
        }
        for label, test in flag.items():
            counts[label] += test
            if test and label not in witnesses:
                witnesses[label] = dict(supports=supports, carriers=C, missing=labels(missing), holders=H,
                                        whole_stage_essential=essential, reductions=reductions)
        if len(absent) > 1:
            witnesses["multiple missing words"] = dict(supports=supports, carriers=C, missing=labels(missing),
                holders=H, each_law_restores=[labels(missing & ~T.image(C, allow)) for allow in T.deleted])
    return counts, witnesses


def read_rows(pattern):
    result = {}
    for f in sorted((STUDY / "out").glob(pattern)):
        for line in f.open():
            row = json.loads(line)
            rank = int(row["start"].split()[-1])
            if rank in result:
                raise ValueError(f"duplicate recorded source rank {rank}")
            result[rank] = row
    return result


def audit_cases(archive, ranks, expected, cap):
    case_results = []
    totals, totals_aux, before, starts, strict_witnesses = Counter(), Counter(), Counter(), Counter(), {}
    discrepancies = []
    archive_examples = 0
    for rank in ranks:
        support = archive[rank]
        grown = advance(support)
        row = {"archive_rank": rank, "rounds": []}
        for rd, supports in enumerate((support, grown.supports) if grown.status == "funded" else (support,)):
            truth = Truth(supports) if rd == 0 else None
            records = stage_records(supports, cap, carry_reader=truth)
            good, base, aux = summaries(supports, records, born=len(support) if rd else 0)
            raw = expected[rank][f"round {rd}"]
            expected_base = {k: v for k, v in raw.items() if k != "examples"}
            if base != expected_base:
                discrepancies.append([rank, rd, {k: [v, expected_base.get(k)] for k, v in base.items()
                                                  if v != expected_base.get(k)}])
            for item in raw["examples"]:
                C = tuple(tuple(c) for c, lab in item["readings"])
                match = good.get(C)
                if (match is None or list(match[0]) != item["holders"] or labels(match[1]) != item["missing"]
                        or item["stage missing"] != item["missing"] or not item["same relation on the stage"]
                        or item["read at a knot of the stage"] or any(lab != "=" for c, lab in item["readings"])):
                    discrepancies.append([rank, rd, "archived example", item])
                archive_examples += 1
            row["rounds"].append({"round": rd, **base, "alternative_holder_checks": dict(aux)})
            totals_aux.update(aux)
            totals[f"round {rd} bonds"] += len(good)
            totals[f"round {rd} stages"] += 1
            totals[f"round {rd} stages with bonds"] += bool(good)
            totals["violations of the count bound"] += base["bound fails"]
            totals["bonds with more than one missing word"] += sum(
                n for c, n in base["missing counts"].items() if int(c) > 1)
            if rd:
                totals["round 1 bonds with a birth"] += base["with a birth among the holders"]
                totals["round 1 stages with a birth bond"] += bool(base["with a birth among the holders"])
                totals["round 1 stages with shared readings"] += bool(base["readings in two or more bonds"])
            else:
                extra, witnesses = extra_checks(supports, good, records, truth)
                row["before_growth_controls"] = dict(extra)
                before.update(extra)
                starts.update(k for k, n in extra.items() if n)
                for k, example in witnesses.items():
                    strict_witnesses.setdefault(k, dict(archive_rank=rank, **example))
        if ("not funded" == expected[rank]["round 1"]) != (grown.status != "funded"):
            discrepancies.append([rank, "different funding"])
        case_results.append(row)
    return {"totals": dict(totals), "alternative_holders": dict(totals_aux),
            "before_growth_control_bonds": dict(before), "before_growth_control_starts": dict(starts),
            "witnesses": strict_witnesses, "archived_examples_compared": archive_examples,
            "discrepancies": discrepancies, "cases": case_results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", type=int, choices=(4, 5), default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--ranks", type=int, nargs="+")
    parser.add_argument("--out", type=Path)
    options = parser.parse_args()
    started = time.perf_counter()
    archive = inputs()
    pilot = set(random.Random(1).sample(range(len(archive)), 10))
    available = sorted(set(range(len(archive))) - pilot)
    expected_order = sorted(random.Random(20261127).sample(available, 1000))
    if options.cap == 5:
        expected_order = expected_order[::10]
    raw = read_rows("census_nae_m5.jsonl" if options.cap == 5 else "census_nae_[0-9].jsonl")
    assert expected_order == sorted(raw)
    ranks = options.ranks or expected_order[:options.limit]
    result = audit_cases(archive, ranks, raw, options.cap)
    result["config"] = {"holder_cap": options.cap, "ranks": ranks, "source_count": len(archive),
                        "excluded_pilot": sorted(pilot), "sample_seed": 20261127,
                        "holder_types_tabulated": enumerate_type.cache_info().currsize}
    result["seconds"] = round(time.perf_counter() - started, 4)
    if options.out:
        options.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({k: result[k] for k in (
        "totals", "alternative_holders", "before_growth_control_bonds", "before_growth_control_starts",
        "archived_examples_compared", "discrepancies", "seconds")}, indent=1))


if __name__ == "__main__":
    main()

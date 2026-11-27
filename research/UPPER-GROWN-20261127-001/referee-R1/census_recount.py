"""Independently replay the frozen census and its full and capped searches."""

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
import ctypes
from functools import cache
from hashlib import sha256
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ARCHIVE = RESEARCH / "FORBID-EDITS-20261126-001/starts.json"
GROWTH = RESEARCH / "NAE-LAYER-20261127-001/referee-R1"
sys.path.insert(0, str(GROWTH))
from growth_rule import advance, supports_of


WORD = ctypes.c_uint64
POINTER = ctypes.c_void_p
WORD_POINTER = ctypes.POINTER(WORD)
POPULATION = 7075
BOX_FIELDS = (
    "boxes", "boxes read", "upper missing exactly one", "a birth needed", "reads a born distinction",
)
RING = ((0, 1, 3), (1, 2, 4), (0, 2, 5))
PREDECESSOR = RESEARCH / "RING-BOND-20261127-001"


def mask(names):
    return sum(1 << x for x in names)


def names(bits):
    return tuple(x for x in range(bits.bit_length()) if bits & (1 << x))


class Bond(ctypes.Structure):
    _fields_ = (("carriers", WORD * 3), ("missing", WORD))


class Search:
    def __init__(self, library):
        self.library = ctypes.CDLL(str(library))
        signatures = {
            "bonds": (POINTER, ctypes.c_uint, ctypes.c_uint, WORD_POINTER, ctypes.c_bool),
            "bond_data": (ctypes.POINTER(Bond), POINTER),
            "bond_count": (ctypes.c_size_t, POINTER),
            "bond_counts": (WORD_POINTER, POINTER),
            "bond_release": (None, POINTER),
            "boxes": (POINTER, ctypes.c_size_t, ctypes.POINTER(Bond)),
            "box_data": (WORD_POINTER, POINTER),
            "box_count": (ctypes.c_size_t, POINTER),
            "box_pairs": (WORD, POINTER),
            "box_release": (None, POINTER),
        }
        for function, (result, *arguments) in signatures.items():
            call = getattr(self.library, "census_" + function)
            call.restype = result
            call.argtypes = arguments
        self.holder_cache = {}

    @contextmanager
    def finite_bonds(self, supports, *, every_law=False):
        masks = tuple(map(mask, supports))
        n = max(masks).bit_length()
        if n > 24:
            raise ValueError(f"Finite table is capped at 24 distinctions, received {n}")
        encoded = (WORD * len(masks))(*masks)
        handle = self.library.census_bonds(n, len(masks), encoded, every_law)
        try:
            number = self.library.census_bond_count(handle)
            data = self.library.census_bond_data(handle)
            allowed, unread, triples = self.library.census_bond_counts(handle)[:3]
            yield data, number, {"allowed states": 2 * allowed, "unread readings": unread,
                                 "pair-free disjoint carrier triples": triples}
        finally:
            self.library.census_bond_release(handle)

    def boxes(self, bonds, number):
        handle = self.library.census_boxes(number, bonds)
        try:
            number = self.library.census_box_count(handle)
            data = self.library.census_box_data(handle)
            pairs = self.library.census_box_pairs(handle)
            return [tuple(data[6 * i:6 * (i + 1)]) for i in range(number)], pairs
        finally:
            self.library.census_box_release(handle)

    def holder_bonds(self, incidence, count):
        key = incidence, count
        if key not in self.holder_cache:
            supports = tuple(tuple(x for x, h in enumerate(incidence) if h & (1 << k))
                             for k in range(count))
            with self.finite_bonds(supports, every_law=True) as (data, number, _):
                self.holder_cache[key] = tuple((tuple(map(names, b.carriers)), b.missing) for b in data[:number])
        return self.holder_cache[key]

    def mapped_holder_bonds(self, support_groups):
        incidence = defaultdict(int)
        for i, row in enumerate(support_groups):
            for x in row:
                incidence[x] |= 1 << i
        if len(incidence) < 6 or sum(i.bit_count() == 1 for i in incidence.values()) > 9:
            return
        count = len(support_groups)
        key, transform = canonical_holder(tuple(sorted(incidence.values())), count)
        lift = tuple(sorted(incidence, key=lambda x: (transform[incidence[x]], x)))
        for carriers, missing in self.holder_bonds(key, count):
            moved = tuple(mask(lift[x] for x in c) for c in carriers)
            order = tuple(sorted(range(3), key=moved.__getitem__))
            yield tuple(moved[i] for i in order), permute_words(missing, order)


@contextmanager
def compiled_search():
    # The compiler's inputs, output, and scratch stay in the referee folder.
    with TemporaryDirectory(prefix="census-scratch-", dir=HERE) as scratch:
        target = Path(scratch) / "search.so"
        environment = dict(os.environ, TMPDIR=scratch)
        subprocess.run(["g++", "-std=c++20", "-O3", "-march=native", "-fPIC", "-shared",
                        str(HERE / "census_search.cpp"), "-o", str(target)], check=True, env=environment)
        yield Search(target)


@cache
def canonical_holder(incidence, count):
    def translate(order):
        return {old: sum(((old >> index) & 1) << new for new, index in enumerate(order))
                for old in set(incidence)}

    choices = (translate(order) for order in permutations(range(count)))
    canonical = min(choices, key=lambda trans: tuple(sorted(trans[x] for x in incidence)))
    return tuple(sorted(canonical[x] for x in incidence)), canonical


@cache
def permute_words(missing, order):
    result = 0
    for word in range(8):
        if missing & (1 << word):
            code = sum(((word >> (2 - old)) & 1) << (2 - new) for new, old in enumerate(order))
            result |= 1 << code
    return result


def connected_holders(supports, maximum):
    columns = tuple(map(mask, supports))
    neighbours = ({j for j, b in enumerate(columns) if i != j and a & b}
                  for i, a in enumerate(columns))
    neighbours = tuple(neighbours)
    frontier = {(i,) for i in range(len(supports))}
    for _ in range(2, maximum + 1):
        frontier = {tuple(sorted((*holder, new))) for holder in frontier
                    for new in set.union(*(neighbours[i] for i in holder)).difference(holder)}
        yield from sorted(frontier)


def nae_clauses(variables):
    return [list(variables), [-v for v in variables]]


def agreement_clauses(out, variables):
    for word in product((False, True), repeat=len(variables)):
        agrees = all(x == word[0] for x in word)
        yield [*(-v if x else v for x, v in zip(word, variables, strict=True)), out if agrees else -out]


class StageQueries:
    """One query instance with two copies of the same allowed-state relation."""

    def __init__(self, supports, *, deletions=False):
        self.solver = Solver(name="g4")
        n = 1 + max(max(row) for row in supports)
        self.variables = [tuple(range(1 + k * n, 1 + (k + 1) * n)) for k in range(2)]
        self.last = 2 * n
        self.guards = tuple(self.fresh() for _ in supports)
        self.rules = tuple(self.fresh() for _ in supports) if deletions else ()
        self.readings = {}
        self.determined = {}
        for i, row in enumerate(supports):
            prefix = [-self.rules[i]] if deletions else []
            for xs in self.variables:
                for clause in nae_clauses([xs[x] for x in row]):
                    self.solver.add_clause(prefix + clause)
            for x in row:
                a, b = (xs[x] for xs in self.variables)
                self.solver.add_clause([-self.guards[i], -a, b])
                self.solver.add_clause([-self.guards[i], a, -b])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()

    def fresh(self):
        self.last += 1
        return self.last

    def reading(self, carrier):
        if carrier not in self.readings:
            pair = []
            for xs in self.variables:
                out = self.fresh()
                pair.append(out)
                for clause in agreement_clauses(out, [xs[x] for x in names(carrier)]):
                    self.solver.add_clause(clause)
            self.readings[carrier] = tuple(pair)
        return self.readings[carrier]

    def missing(self, observables, skip=None):
        assumptions = [rule if i != skip else -rule for i, rule in enumerate(self.rules)]
        return sum(1 << word for word in range(8) if not self.solver.solve(assumptions=assumptions + [
            v if word & (4 >> i) else -v for i, v in enumerate(observables)]))

    def read_at_one(self, carrier):
        if carrier not in self.determined:
            left, right = self.reading(carrier)
            self.determined[carrier] = any(not self.solver.solve(assumptions=[*self.rules, guard, left, -right])
                                           for guard in self.guards)
        return self.determined[carrier]

    def upper_word(self, box):
        upper = []
        for a, b in zip(box[::2], box[1::2], strict=True):
            left, right = self.reading(a >> 1)[0], self.reading(b >> 1)[0]
            agreement = self.fresh()
            for clause in agreement_clauses(agreement, [left, right]):
                self.solver.add_clause(clause)
            upper.append(agreement if (a ^ b) & 1 else -agreement)
        return upper


def local_bonds(search, supports):
    candidates = defaultdict(list)
    for holder in connected_holders(supports, 4):
        for carriers, missing in search.mapped_holder_bonds(tuple(supports[i] for i in holder)):
            candidates[carriers].append(missing)
    registered = []
    additional = []
    with StageQueries(supports) as stage:
        for carriers, certificates in candidates.items():
            if any(stage.read_at_one(c) for c in carriers):
                continue
            missing = stage.missing([stage.reading(c)[0] for c in carriers])
            if missing == certificates[0]:
                registered.append(Bond((WORD * 3)(*carriers), missing))
            elif missing in certificates:
                additional.append(Bond((WORD * 3)(*carriers), missing))
    return registered, additional, len(candidates)


def box_findings(supports, boxes, *, before, n_source):
    details = []
    if not boxes:
        return details
    with StageQueries(supports, deletions=True) as stage:
        for box in boxes:
            upper = stage.upper_word(box)
            missing = stage.missing(upper)
            needed = [i for i in range(len(supports)) if stage.missing(upper, skip=i) != missing]
            details.append({
                "box": [[(names(code >> 1), code & 1) for code in box[q:q + 2]] for q in (0, 2, 4)],
                "upper missing": [f"{word:03b}" for word in range(8) if missing & (1 << word)],
                "laws needed": needed,
                "a birth needed": any(i >= n_source for i in needed),
                "reads a born distinction": (any((code >> 1).bit_length() > before for code in box)),
            })
    return details


def summarize_search(search, supports, before, n_source, *, full):
    started = monotonic()
    extras = {}
    if full:
        with search.finite_bonds(supports) as (data, count, diagnostics):
            bonds_seconds = monotonic() - started
            boxes, pairs = search.boxes(data, count)
    else:
        registered, additional, candidates = local_bonds(search, supports)
        bonds_seconds = monotonic() - started
        diagnostics = {"distinct holder candidates": candidates}
        count = len(registered)
        boxes, pairs = search.boxes((Bond * count)(*registered), count)
        extras["additional bonds under any qualifying holder"] = len(additional)
        if additional:
            all_bonds = registered + additional
            new_boxes, new_pairs = search.boxes((Bond * len(all_bonds))(*all_bonds), len(all_bonds))
            extras["boxes under any qualifying holder"] = len(new_boxes)
            extras["qualifying first pairs under any holder"] = new_pairs
            extras["box details under any qualifying holder"] = box_findings(
                supports, new_boxes, before=before, n_source=n_source,
            )
    details = box_findings(supports, boxes, before=before, n_source=n_source)
    return {
        "bonds": count,
        "boxes": len(boxes),
        "boxes read": len(details),
        "upper missing exactly one": sum(len(row["upper missing"]) == 1 for row in details),
        "a birth needed": sum(row["a birth needed"] for row in details),
        "reads a born distinction": sum(row["reads a born distinction"] for row in details),
        "qualifying first pairs": pairs,
        "bonds seconds": round(bonds_seconds, 6),
        "total seconds": round(monotonic() - started, 6),
        "box details": details,
        **diagnostics,
        **extras,
    }


def compare_literal(search, supports):
    """Cross-check a small table by screening each triple with explicit states."""
    n = 1 + max(max(row) for row in supports)
    allowed = [word for word in product((False, True), repeat=n)
               if all(any(word[x] != word[knot[0]] for x in knot[1:]) for knot in supports)]
    readings = {}
    for length in (2, 3):
        for carrier in combinations(range(n), length):
            truths = tuple(all(word[x] == word[carrier[0]] for x in carrier[1:]) for word in allowed)
            for knot in supports:
                local = [set(), set()]
                for word, value in zip(allowed, truths, strict=True):
                    local[value].add(tuple(word[x] for x in knot))
                if not local[0].intersection(local[1]):
                    break
            else:
                readings[mask(carrier)] = truths
    literal = {}
    for carriers in combinations(sorted(readings), 3):
        a, b, c = carriers
        if a & b or a & c or b & c:
            continue
        words = set(zip(*(readings[x] for x in carriers), strict=True))
        if len(words) == 8 or any(len({(w[i], w[j]) for w in words}) < 4 for i, j in combinations(range(3), 2)):
            continue
        literal[carriers] = sum(1 << w for w in set(range(8)) - {4 * a + 2 * b + c for a, b, c in words})
    with search.finite_bonds(supports) as (data, number, _):
        compiled = {tuple(bond.carriers): bond.missing for bond in data[:number]}
    assert compiled == literal
    return len(literal)


def source_controls(search):
    first = advance(RING).supports
    stages = [dict(literal_bonds=compare_literal(search, stage),
                   **summarize_search(search, stage, 6, len(RING), full=True)) for stage in (RING, first)]
    tested = summarize_search(search, known_closed_witness(), 18, 12, full=True)
    assert tested["boxes"] == 90 and tested["upper missing exactly one"] == 90
    assert all(len(record["laws needed"]) == 12 for record in tested["box details"])
    tested["box details"] = tested["box details"][:1]
    return {"three-knot ring starts and first round": stages, "earlier twelve-knot positive witness": tested}


def known_closed_witness():
    witness = json.loads((PREDECESSOR / "referee-R1/layer_witness.json").read_text())
    return tuple(tuple(row) for row in witness["source_knots_not_all_equal"])


def signed_pattern_control(search):
    groups = (((3, 0), (12, 1)), ((48, 1), (192, 0)), ((768, 0), (3072, 1)))
    bonds = [Bond((WORD * 3)(a, b, c), 1 << (4 * va + 2 * vb + vc))
             for (a, va), (b, vb), (c, vc) in product(*groups)]
    count = len(bonds)
    found, _ = search.boxes((Bond * count)(*bonds), count)
    removed, _ = search.boxes((Bond * (count - 1))(*bonds[1:]), count - 1)
    bonds[0].missing = bonds[0].missing << 1
    changed, _ = search.boxes((Bond * count)(*bonds), count)
    assert found == [tuple((carrier << 1) | sign for group in groups for carrier, sign in group)]
    assert not removed and not changed
    return {"carriers with missing values": [[(names(mask), value) for mask, value in g] for g in groups],
            "signed pattern": len(found), "one lower word changed": len(changed),
            "one lower bond removed": len(removed)}


def ring_report(search, rounds):
    raw_path = PREDECESSOR / "out/ring.json"
    raw = json.loads(raw_path.read_text())["full"]
    supports = RING
    rows = []
    for stage in range(rounds + 1):
        n, knot_count = stage_sizes(supports)
        replay = summarize_search(search, supports, 6, len(RING), full=True)
        archive = raw[stage]
        assert (archive["round"], archive["knots"], archive["distinctions"], archive["bonds"]) == (
            stage, knot_count, n, replay["bonds"])
        assert replay["boxes"] == 0
        rows.append({"round": stage, "knots": knot_count, "distinctions": n,
                     "supports": supports, "archived bonds": archive["bonds"], **replay})
        if stage < rounds:
            step = advance(supports)
            assert step.status == "funded"
            supports = step.supports
    commands = ["ulimit -v 1750000", "export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1",
                f'referee_dir={HERE.relative_to(HERE.parents[2])}',
                '.venv/bin/python -B "$referee_dir/census_recount.py" --mode ring --rounds 2 '
                '--out "$referee_dir/census_ring_pilot.json"',
                '.venv/bin/python -B "$referee_dir/census_recount.py" --mode ring --rounds 4 '
                '--out "$referee_dir/census_ring.json"']
    return {"compared archived counts": str(raw_path.relative_to(HERE.parents[2])), "rounds": rows,
            "signed product control": signed_pattern_control(search), "rerun from repository root": commands}


def read_roster():
    data = ARCHIVE.read_bytes()
    archive = json.loads(data)
    assert len(archive) == POPULATION
    pilot = sorted(random.Random(1).sample(range(len(archive)), 10))
    file = STUDY / "pilot/p10.jsonl"
    assert pilot == [rank_of(json.loads(line)) for line in file.read_text().splitlines()]
    excluded = set(pilot)
    sample = [i for i in range(len(archive)) if i not in excluded]
    sample = sorted(random.Random(20261128).sample(sample, 1000))
    raw = {}
    for i in range(8):
        path = STUDY / "out" / f"census_{i}.jsonl"
        loaded = [json.loads(line) for line in path.read_text().splitlines()]
        assert [rank_of(r) for r in loaded] == sample[i::8]
        raw.update({rank_of(r): r for r in loaded})
    return archive, pilot, sample, raw, sha256(data).hexdigest()


def rank_of(row):
    label, rank = row["start"].split()
    assert label == "census"
    return int(rank)


def stage_sizes(supports):
    roster = set(x for row in supports for x in row)
    assert roster == set(range(len(roster)))
    return len(roster), len(supports)


def rebuild_stages(source):
    stages = [source]
    steps = []
    for _ in range(2):
        step = advance(stages[-1])
        steps.append(step)
        if step.status != "funded":
            break
        stages.append(step.supports)
    return stages, steps


def basic_record(rank, stage, supports, raw, steps):
    n, knot_count = stage_sizes(supports)
    expected = {"round": stage, "distinctions": n, "knots": knot_count, "search": "full" if n <= 19 else "local"}
    assert all(raw[key] == value for key, value in expected.items()), (rank, expected, raw)
    stage_key = sha256(json.dumps(supports, separators=(",", ":")).encode()).hexdigest()
    raw_fields = ("bonds",) + BOX_FIELDS
    return {
        "archive rank": rank, **expected,
        "raw": {key: raw[key] for key in raw_fields},
        "raw examples": len(raw["examples"]),
        "supports sha256": stage_key,
        "births this round": len(steps[stage - 1].births) if stage else 0,
        "next round status": steps[stage].status if stage < len(steps) else "outside the frozen horizon",
    }


def audit(args, search):
    archive, pilot, sample, raw, digest = read_roster()
    selection = sorted(set(args.ranks)) if args.ranks else sample
    assert set(selection).issubset(sample)
    records = []
    totals = defaultdict(Counter)
    discrepancies = []
    for rank in selection:
        source = supports_of(archive[rank])
        stages, steps = rebuild_stages(source)
        assert len(stages) == len(raw[rank]["rounds"]), (rank, len(stages), raw[rank])
        before = stage_sizes(source)[0]
        for stage, (supports, old) in enumerate(zip(stages, raw[rank]["rounds"], strict=True)):
            row = basic_record(rank, stage, supports, old, steps)
            census = totals[f"round {stage}, {row['search']}"]
            census["archive stages"] += 1
            census["at least twelve distinctions and eight archived bonds"] += (
                row["distinctions"] >= 12 and old["bonds"] >= 8)
            census["archived bonds"] += old["bonds"]
            census["archived boxes"] += old["boxes"]
            census["archived boxes read"] += old["boxes read"]
            query = (args.minimum <= row["distinctions"] <= args.maximum and
                     (args.mode == "archive" or row["search"] == args.mode or
                      (args.mode == "upgrade" and row["search"] == "local")))
            if query:
                full = row["search"] == "full" or args.mode == "upgrade"
                observed = summarize_search(search, supports, before, len(source), full=full)
                row["replay"] = observed
                row["replay search"] = "full" if full else "local"
                census["independently searched stages"] += 1
                census["independent bonds"] += observed["bonds"]
                census["independent boxes"] += observed["boxes"]
                census["independent boxes needing a birth"] += observed["a birth needed"]
                census["any qualifying first pair"] += observed["qualifying first pairs"] > 0
                census["qualifying first pairs"] += observed["qualifying first pairs"]
                census["additional bonds under any qualifying holder"] += observed.get(
                    "additional bonds under any qualifying holder", 0)
                census["boxes under any qualifying holder"] += observed.get(
                    "boxes under any qualifying holder", observed["boxes"])
                census["total search seconds"] += observed["total seconds"]
                if args.mode != "upgrade":
                    differences = {field: [old[field], observed[field]] for field in ("bonds",) + BOX_FIELDS
                                   if old[field] != observed[field]}
                    if differences:
                        discrepancies.append({"rank": rank, "round": stage, "fields": differences})
            else:
                census["independent search not run"] += 1
            records.append(row)
    return {"archive sha256": digest, "archive size": len(archive), "excluded pilot ranks": pilot,
            "frozen selected starts": len(sample), "reconstructed starts": len(selection),
            "size interval": [args.minimum, args.maximum], "mode": args.mode,
            "discrepancies": discrepancies, "stage totals": totals, "records": records}


def denominator_report():
    path = HERE / "census_recount.json"
    replay = json.loads(path.read_text())
    assert replay["mode"] == "archive" and not replay["discrepancies"]
    cells = defaultdict(Counter)
    for row in replay["records"]:
        census = cells[f"round {row['round']}, {row['search']}"]
        coarse = row["distinctions"] >= 12 and row["raw"]["bonds"] >= 8
        pairs = row["replay"]["qualifying first pairs"]
        census["stages"] += 1
        census["stages with at least twelve distinctions and eight bonds"] += coarse
        census["stages with a qualifying first pair"] += pairs > 0
        census["stages passing both conditions"] += coarse and pairs > 0
        census["qualifying first pairs among stages passing both conditions"] += pairs if coarse else 0
        census["boxes read for birth-law deletion"] += row["replay"]["boxes read"]
    totals = Counter()
    for counts in cells.values():
        totals.update(counts)
    return {"source": path.name, "definition of a qualifying first pair":
            "Two signed readings have disjoint carriers and at least four common signed links from single-word "
            "lower bonds. Each reading in a common link exceeds the smaller reading of the first pair in the "
            "search order. The count precedes checking whether the common links supply four disjoint readings "
            "in the required pattern.",
            "counts by round and archived search": cells, "totals": totals}


def superset_report(args, search):
    # Import only the independent certificate generator being tested. The
    # comparison uses the full finite-state scan before any holder selection.
    from large_cores import clauses
    from large_search import candidates, refine, structural_boxes

    archive, _, sample, _, digest = read_roster()
    assert args.ranks and set(args.ranks).issubset(sample)
    path = HERE / "large_stages.json"
    reported = {(row["start"], row["round"]): row for row in json.loads(path.read_text())["rows"]}
    rows = []
    for rank in sorted(set(args.ranks)):
        stages, _ = rebuild_stages(supports_of(archive[rank]))
        for stage, supports in enumerate(stages):
            n, knots = stage_sizes(supports)
            if not args.minimum <= n <= args.maximum:
                continue
            started = monotonic()
            certificates, diagnostics = clauses(supports)
            triples, signed = candidates(supports, certificates)
            indices = {signed_reading: i for i, signed_reading in enumerate(signed)}
            missing_counter = Counter()
            missed = []
            with search.finite_bonds(supports) as (bonds, count, _):
                full_boxes, _ = search.boxes(bonds, count)
                for i in range(count):
                    bond = bonds[i]
                    for word in range(8):
                        if not bond.missing & (1 << word):
                            continue
                        missing_counter[f"{word:03b}"] += 1
                        lower_word = tuple((c, (word >> (2 - p)) & 1) for p, c in enumerate(bond.carriers))
                        addressed = tuple(sorted(indices.get(item, -1) for item in lower_word))
                        if addressed not in triples:
                            missed.append([(names(c), v) for c, v in lower_word])
            surviving, disjoint, sizes = refine(triples, signed)
            structural = sum(1 for _ in structural_boxes(surviving, signed, disjoint))
            record = {"archive rank": rank, "round": stage, "distinctions": n, "knots": knots,
                      "full lower bonds": count, "full signed missing words by value": dict(sorted(missing_counter.items())),
                      "signed missing words absent from the superset": len(missed), "first missing from superset": missed[:3],
                      "full boxes": len(full_boxes), "superset structural boxes": structural,
                      "signed triples before and after disjoint alternatives": sizes,
                      "total seconds": round(monotonic() - started, 6), **diagnostics}
            other = reported[rank, stage]
            for field in ("distinctions", "knots", "signed triples before and after disjoint alternatives"):
                assert record[field] == other[field], (rank, stage, field)
            assert structural == other["structural_boxes"]
            assert len(full_boxes) <= structural
            rows.append(record)
    missing_cases = [{"archive rank": row["archive rank"], "round": row["round"],
                      "missing words": row["signed missing words absent from the superset"]}
                     for row in rows if row["signed missing words absent from the superset"]]
    return {"archive sha256": digest, "compared superset result": path.name, "rows": rows,
            "discrepancies": missing_cases}


def superset_positive_control(search):
    from large_cores import ordered_shape, partial_certificates
    from large_search import candidates, refine, structural_boxes

    def groups(box):
        return frozenset(frozenset(box[i:i + 2]) for i in (0, 2, 4))

    started = monotonic()
    witness = json.loads((PREDECESSOR / "referee-R1/layer_witness.json").read_text())
    supports = tuple(tuple(knot) for knot in witness["source_knots_not_all_equal"])
    witness_readings = tuple((mask(carrier) << 1) | 1 for carrier in witness["lower_carriers_in_A0_A1_B0_B1_C0_C1_order"])
    witness_box = groups(witness_readings)
    with search.finite_bonds(supports) as (bonds, count, _):
        exact_boxes, _ = search.boxes(bonds, count)
    assert witness_box in {groups(box) for box in exact_boxes}
    holder_sets = [record["source_laws_whose_separate_deletion_restores_111"] for record in witness["first_bonds"]]
    certificates = set()
    holder_seconds = []
    for rows in holder_sets:
        holder_start = monotonic()
        shape, lift = ordered_shape(tuple(supports[i] for i in rows))
        for certificate in partial_certificates(shape):
            certificates.add(tuple(sorted((mask(lift[i] for i in group), value) for group, value in certificate)))
        holder_seconds.append(round(monotonic() - holder_start, 6))
    triples, signed = candidates(supports, certificates)
    indices = {((carrier << 1) | value): i for i, (carrier, value) in enumerate(signed)}
    expected = {tuple(sorted(indices[reading] for reading in selected))
                for selected in product(witness_readings[0:2], witness_readings[2:4], witness_readings[4:6])}
    surviving, disjoint, sizes = refine(triples, signed)
    assert expected <= triples and expected <= set(surviving)
    possible = {groups(tuple((signed[i][0] << 1) | signed[i][1] for i in box))
                for box in structural_boxes(surviving, signed, disjoint)}
    retained = sum(groups(box) in possible for box in exact_boxes)
    assert witness_box in possible and len(exact_boxes) == 90
    return {"source-law subsets checked": holder_sets, "seconds by source-law subset": holder_seconds,
            "certificates on these subsets": len(certificates), "chosen missing words in candidates": len(expected),
            "chosen missing words retained after pruning": len(expected), "chosen box recovered": True,
            "full lower bonds": count, "full boxes in the finite truth table": len(exact_boxes),
            "full boxes recovered from these subsets": retained, "structural box candidates": len(possible),
            "signed triples before and after disjoint alternatives": sizes,
            "total seconds": round(monotonic() - started, 6)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("archive", "full", "local", "metadata", "upgrade", "ring", "superset",
                                           "denominators"),
                        default="archive")
    parser.add_argument("--minimum", type=int, default=0)
    parser.add_argument("--maximum", type=int, default=38)
    parser.add_argument("--rounds", type=int, choices=range(5), default=4)
    parser.add_argument("--ranks", type=int, nargs="+")
    parser.add_argument("--controls", action="store_true")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    assert args.out.resolve().parent == HERE and args.out.name.startswith("census"), args.out
    if args.mode in ("upgrade", "superset") and not 20 <= args.minimum <= args.maximum <= 24:
        parser.error("full-table comparisons above the original cutoff take a size interval between 20 and 24")
    started = monotonic()
    if args.mode == "metadata" and not args.controls:
        result = audit(args, None)
    elif args.mode == "denominators":
        result = denominator_report()
    else:
        with compiled_search() as search:
            if args.mode == "ring":
                result = ring_report(search, args.rounds)
            elif args.mode == "superset":
                result = superset_report(args, search)
            else:
                result = audit(args, search)
            if args.controls:
                result["independent controls"] = source_controls(search)
                if args.mode == "superset":
                    result["superset positive control"] = superset_positive_control(search)
    result["elapsed seconds"] = round(monotonic() - started, 6)
    result["peak resident kibibytes"] = max(resource.getrusage(who).ru_maxrss
                                           for who in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN))
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    rows = result.get("records", result.get("rounds", result.get("rows", [])))
    count = result["totals"]["stages"] if args.mode == "denominators" else len(rows)
    print(f"{count} stages checked, {len(result.get('discrepancies', []))} disagreements, "
          f"{result['elapsed seconds']} seconds, {result['peak resident kibibytes']} KiB", flush=True)


if __name__ == "__main__":
    main()

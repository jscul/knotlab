"""Exact lower bonds and signed upper forms on the newly closed census stages."""
import argparse
import ctypes
import json
import resource
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
TRIPLES = tuple(product(range(2), repeat=3))
PAIRS = tuple(product(range(2), repeat=2))
FOUR_KINDS = ("alternating", "paired", "one_and_three")


class Bond(ctypes.Structure):
    _fields_ = [(key, ctypes.c_uint32) for key in ("a", "b", "c", "image")]


def kernel():
    lib = ctypes.CDLL(str(HERE / "closed_bonds.so"))
    masks = ctypes.POINTER(ctypes.c_uint32)
    lib.closed_enumerate.argtypes = [ctypes.c_int, ctypes.c_int, masks, ctypes.c_int, masks]
    lib.closed_results.restype = ctypes.POINTER(Bond)
    lib.closed_unread.restype = masks
    return lib


def support_mask(names):
    return sum(1 << x for x in names)


def signed_triple(a, b, c):
    return tuple(sorted((a, b, c)))


def lower_bonds(lib, knots, n, chosen):
    carriers = [support_mask(s) for size in (2, 3) for s in combinations(range(n), size)]
    if chosen is not None:
        carriers = list(map(support_mask, chosen))
    def array(values):
        return (ctypes.c_uint32 * len(values))(*values)
    count = lib.closed_enumerate(n, len(knots), array(list(map(support_mask, knots))),
                                 len(carriers), array(carriers))
    unreads = lib.closed_unread()[:lib.closed_unread_count()]
    histogram = Counter()
    clauses = set()
    for bond in lib.closed_results()[:count]:
        missing = 255 ^ bond.image
        histogram[missing.bit_count()] += 1
        if missing.bit_count() == 1:
            forbidden = missing.bit_length() - 1
            signed = [2 * support + ((forbidden >> shift) & 1)
                      for support, shift in zip((bond.a, bond.b, bond.c), (2, 1, 0))]
            clauses.add(tuple(sorted(signed)))
    return lib.closed_state_count(), unreads, count, histogram, clauses


def disjoint_packing(unread, n):
    by_member = [[support for support in unread if support & (1 << x)] for x in range(n)]
    @cache
    def fits(available, needed):
        if needed == 0:
            return True
        if available.bit_count() < 2 * needed:
            return False
        first = available & -available
        if fits(available ^ first, needed):
            return True
        return any(s & available == s and fits(available ^ s, needed - 1)
                   for s in by_member[first.bit_length() - 1])
    return fits


def subset_masks(mask, sizes):
    part = mask
    while part:
        if part.bit_count() in sizes:
            yield part
        part = (part - 1) & mask


def raw_span(clause):
    a, b, c = clause
    return (a | b | c) >> 1


def ordered_pairs(groups):
    return tuple(sorted(tuple(sorted(pair)) for pair in groups))


def lower_choices(groups):
    return {p: signed_triple(*(pair[i] for pair, i in zip(groups, p))) for p in TRIPLES}


def possibilities(groups, lower):
    """Get each conjunction pair and all assignments of one of its readings per clause."""
    options = lower_choices(groups)
    present = {bits for bits, clause in options.items() if clause in lower}
    if len(present) < 4:
        return
    for central in range(3):
        sides = [i for i in range(3) if i != central]
        at = defaultdict(list)
        for bits in present:
            at[(bits[sides[0]], bits[sides[1]])].append(bits)
        if len(at) != 4:
            continue
        for selected in product(*(at[bc] for bc in PAIRS)):
            code = tuple(p[central] for p in selected)
            if len(set(code)) != 2:
                continue
            if sum(code) != 2:
                kind = "one_and_three"
            elif code[0] == code[3]:
                kind = "alternating"
            else:
                kind = "paired"
            yield kind, central, tuple(options[p] for p in selected)


def arrangements(clauses, n, can_fit_one):
    """Generate every possible six-reading grouping before testing source images."""
    universe = (1 << n) - 1
    by_span = defaultdict(list)
    by_pair = defaultdict(set)
    by_one = defaultdict(lambda: defaultdict(list))
    for clause in clauses:
        a, b, c = clause
        by_span[raw_span(clause)].append(clause)
        for x, y, z in ((a, b, c), (a, c, b), (b, c, a)):
            by_pair[x, y].add(z)
        for pivot, x, y in ((a, b, c), (b, a, c), (c, a, b)):
            by_one[pivot][(x | y) >> 1].append((x, y))
    groups_found = set()
    disjoint_pairs = 0
    partial_alternating = 0
    partial_with_sixth = 0
    ordered_partial = 0
    # Every box contains two complementary clauses. Every nonconstant four-
    # clause choice except the alternating one has two disjoint clauses too:
    # f(0,0)=f(1,1) and f(0,1)=f(1,0) force an alternating or constant
    # function. Try each pairing across the two disjoint clauses.
    for first in clauses:
        rest = universe ^ raw_span(first)
        for span in subset_masks(rest, (6, 7, 8, 9)):
            for second in by_span.get(span, ()):
                if first >= second:
                    continue
                disjoint_pairs += 1
                for perm in permutations(second):
                    groups = ordered_pairs(zip(first, perm))
                    if groups in groups_found:
                        continue
                    if next(possibilities(groups, clauses), None) is not None:
                        groups_found.add(groups)
    # In each alternating family the two clauses at its least signed reading
    # share only that reading. Their other four supports are disjoint. The
    # other two clauses connect these four readings in pairs and share the
    # sixth signed reading. Check both ways to pair the two sets of two.
    for x, y, z in clauses:
        rest = universe ^ raw_span((x, y, z))
        for span in subset_masks(rest, (4, 5, 6)):
            room = rest ^ span
            if room.bit_count() < 2:
                continue
            for a, b, c in ((x, y, z), (y, x, z), (z, x, y)):
                for d, e in by_one[a].get(span, ()):
                    if (b, c) >= (d, e):
                        continue
                    partial_alternating += 1
                    if not can_fit_one(room):
                        continue
                    partial_with_sixth += 1
                    if min(b, c, d, e) < a:
                        continue
                    ordered_partial += 1
                    for u, v in ((d, e), (e, d)):
                        one = by_pair.get(tuple(sorted((b, u))))
                        two = by_pair.get(tuple(sorted((c, v))))
                        if not one or not two:
                            continue
                        for f in one & two:
                            raw = f >> 1
                            if f > a and (room & raw) == raw:
                                groups_found.add(ordered_pairs(((a, f), (b, v), (c, u))))
    return groups_found, disjoint_pairs, partial_alternating, partial_with_sixth, ordered_partial


class Source:
    def __init__(self, knots, n):
        self.n = n
        self.every = (1 << (1 << n)) - 1
        self.columns = [(self.every // ((1 << (1 << j)) + 1)) << (1 << j)
                        for j in range(n)]
        self.agreements = {}
        self.laws = [self.every ^ self.agree(support_mask(k)) for k in knots]
        self.allowed = self.every
        for law in self.laws:
            self.allowed &= law

    def agree(self, carrier):
        if carrier not in self.agreements:
            columns = [self.columns[i] for i in range(self.n) if carrier & (1 << i)]
            yes = self.every
            for col in columns[1:]:
                yes &= self.every ^ (columns[0] ^ col)
            self.agreements[carrier] = yes
        return self.agreements[carrier]

    def selected(self, signed):
        values = self.agree(signed >> 1)
        return values if signed & 1 else self.every ^ values

    def flips(self, signed):
        raw = signed >> 1
        val = self.selected(signed)
        return [(self.allowed & ~col & (self.allowed >> (1 << j))
                 & (val ^ (val >> (1 << j)))).bit_count()
                for j, col in enumerate(self.columns) if raw & (1 << j)]

    def deletions(self, forbidden):
        counts = []
        for drop in range(len(self.laws)):
            allowed = forbidden
            for i, law in enumerate(self.laws):
                if i != drop:
                    allowed &= law
            counts.append(allowed.bit_count())
        return counts


def cells(source, columns):
    parts = [source]
    for col in columns:
        parts = [split for p in parts for split in (p & ~col, p & col)]
    return parts


def upper_image(source, groups, central, required):
    selected = {s: source.selected(s) for pair in groups for s in pair}
    upper = []
    for i, (a, b) in enumerate(groups):
        u, v = selected[a], selected[b]
        upper.append(u & v if i == central else u | v)
    images = cells(source.allowed, upper)
    if [i for i, part in enumerate(images) if part] != list(range(7)):
        return None
    mixed = []
    for clause in required:
        fixes = cells(source.allowed, [selected[a] for a in clause])
        assert [i for i, part in enumerate(fixes) if part] == list(range(7))
        mixed.append([sum(bool(x & up) and bool(x & ~up) for x in fixes) for up in upper])
    if any(0 in row for row in mixed):
        return None
    sequence = [s for pair in groups for s in pair]
    sensitivity = [source.flips(s) for s in sequence]
    if any(0 in row for row in sensitivity):
        return None
    ordered_clauses = [[sequence.index(s) for s in clause] for clause in required]
    return dict(
        lower_positions_forbidden_111=ordered_clauses,
        conjunction_pair=central,
        selected_signs=[s % 2 for s in sequence],
        six_lower_word_counts=[c.bit_count() for c in cells(source.allowed, [selected[s] for s in sequence])],
        upper_word_counts=[x.bit_count() for x in images],
        mixed_fixes_per_clause_and_upper=mixed,
        allowed_single_changes_per_carrier_member=sensitivity,
        restored_upper_111_on_removing_each_law=source.deletions(upper[0] & upper[1] & upper[2]),
    )


def search(lib, supports, start_knots, last_birth, chosen=None):
    names = sorted({x for knot in supports for x in knot})
    index = {x: i for i, x in enumerate(names)}
    knots = [[index[x] for x in knot] for knot in supports]
    if chosen is not None:
        chosen = [[index[x] for x in carrier] for carrier in chosen]
    n = len(names)
    states, unread, bonds, histogram, clauses = lower_bonds(lib, knots, n, chosen)
    pack = disjoint_packing(unread, n)
    universe = (1 << n) - 1
    eligible = {c for c in clauses if pack(universe ^ raw_span(c), 3)}
    groups, complementary, partial, with_sixth, ordered_partial = arrangements(
        eligible, n, lambda room: pack(room, 1))
    pos = Counter()
    candidates = Counter()
    needs_birth = Counter()
    needs_last = Counter()
    examples = {}
    boxes = []
    source = Source(knots, n) if groups else None
    if source:
        assert states == source.allowed.bit_count()
    def original(s):
        return [x for i, x in enumerate(names) if s & (1 << i)]
    for g in sorted(groups):
        if all(c in eligible for c in lower_choices(g).values()):
            boxes.append(g)
            uppers = [source.selected(a) ^ source.selected(b) for a, b in g]
            image = cells(source.allowed, uppers)
            restored = source.deletions(uppers[0] & uppers[1] & uppers[2])
            if "box" not in examples:
                examples["box"] = dict(source_supports=supports, start_knots=start_knots,
                                       last_birth_knots=last_birth,
                                       carriers_in_pair_order=[original(s >> 1) for p in g for s in p],
                                       selected_signs=[s % 2 for p in g for s in p],
                                       upper_word_counts=[v.bit_count() for v in image],
                                       restored_upper_111_on_removing_each_law=restored)
        for kind, central, required in possibilities(g, eligible):
            candidates[kind] += 1
            w = upper_image(source, g, central, required)
            if w is None:
                continue
            pos[kind] += 1
            restores = w["restored_upper_111_on_removing_each_law"]
            birth = any(restores[start_knots:])
            latest = any(restores[j] for j in last_birth)
            needs_birth[kind] += birth
            needs_last[kind] += latest
            if kind not in examples or (birth and not examples[kind]["a_birth_is_needed"]):
                w.update(source_supports=supports, start_knots=start_knots,
                         last_birth_knots=last_birth, a_birth_is_needed=birth,
                         carriers_in_pair_order=[original(s >> 1) for p in g for s in p])
                examples[kind] = w
    six_fit = pack(universe, 6)
    pack.cache_clear()
    def counts(c):
        return {k: c[k] for k in FOUR_KINDS}
    return dict(knots=len(knots), distinctions=n, allowed=states, unread_carriers=len(unread),
                six_disjoint_unread_carriers=six_fit, bonds=bonds,
                bonds_by_number_of_excluded_words=dict(histogram), single_clauses=len(clauses),
                clauses_by_ones_in_forbidden_original_word=dict(Counter(sum(r & 1 for r in c) for c in clauses)),
                extendible_single_clauses=len(eligible),
                disjoint_signed_clause_pairs=complementary,
                five_reading_candidates_for_alternating=partial,
                five_reading_candidates_with_sixth_unread=with_sixth,
                five_reading_candidates_with_least_common_reading_and_sixth_unread=ordered_partial,
                pairings_admitting_any_connected_four_clause_choice=len(groups),
                boxes=len(boxes), four_clause_choices=counts(candidates),
                four_clause_upper_steps=counts(pos), four_clause_steps_needing_a_birth=counts(needs_birth),
                four_clause_steps_needing_a_last_birth=counts(needs_last)), examples


def archived_counts():
    archives = {}
    for law in ("one_fewer", "arity_floor"):
        for path in sorted((HERE.parent / "out").glob(law + "_*.jsonl")):
            for line in path.read_text().splitlines():
                row = json.loads(line)
                if "start" in row:
                    key = law, int(row["start"].split()[1])
                    assert key not in archives
                    archives[key] = row
    return archives


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def summarize(rows, law):
    data = [r for r in rows if law in r["laws_checked"]]
    return {
        "stages": len(data),
        "stages_with_12_or_more_distinctions": sum(r["distinctions"] >= 12 for r in data),
        "stages_with_six_disjoint_unread_carriers": sum(r["six_disjoint_unread_carriers"] for r in data),
        "stages_with_12_distinctions_and_at_least_8_clauses":
            sum(r["distinctions"] >= 12 and r["single_clauses"] >= 8 for r in data),
        "stages_with_an_extendible_clause": sum(r["extendible_single_clauses"] > 0 for r in data),
        "stages_with_8_extendible_clauses": sum(r["extendible_single_clauses"] >= 8 for r in data),
        "stages_with_4_extendible_clauses": sum(r["extendible_single_clauses"] >= 4 for r in data),
        "stages_with_disjoint_signed_clauses": sum(r["disjoint_signed_clause_pairs"] > 0 for r in data),
        "stages_with_five_reading_candidates_for_alternating":
            sum(r["five_reading_candidates_for_alternating"] > 0 for r in data),
        "stages_with_five_reading_candidates_and_sixth_unread":
            sum(r["five_reading_candidates_with_sixth_unread"] > 0 for r in data),
        "stages_with_box": sum(r["boxes"] > 0 for r in data),
        "boxes": sum(r["boxes"] for r in data),
        "total_bonds": sum(r["bonds"] for r in data),
        "total_single_clauses": sum(r["single_clauses"] for r in data),
        "clauses_by_ones_in_forbidden_original_word":
            {s: sum(r["clauses_by_ones_in_forbidden_original_word"].get(s, 0) for r in data)
             for s in range(4)},
        "total_extendible_single_clauses": sum(r["extendible_single_clauses"] for r in data),
        "total_disjoint_signed_clause_pairs": sum(r["disjoint_signed_clause_pairs"] for r in data),
        "total_five_reading_candidates_for_alternating": sum(r["five_reading_candidates_for_alternating"] for r in data),
        "total_five_reading_candidates_with_sixth_unread":
            sum(r["five_reading_candidates_with_sixth_unread"] for r in data),
        "stages_with_four_clause_choice":
            {k: sum(r["four_clause_choices"][k] > 0 for r in data) for k in FOUR_KINDS},
        "stages_with_four_clause_upper_step":
            {k: sum(r["four_clause_upper_steps"][k] > 0 for r in data) for k in FOUR_KINDS},
        "stages_with_four_clause_step_needing_a_birth":
            {k: sum(r["four_clause_steps_needing_a_birth"][k] > 0 for r in data) for k in FOUR_KINDS},
        "total_four_clause_choices": {k: sum(r["four_clause_choices"][k] for r in data) for k in FOUR_KINDS},
        "total_four_clause_upper_steps": {k: sum(r["four_clause_upper_steps"][k] for r in data) for k in FOUR_KINDS},
        "total_four_clause_steps_needing_a_birth":
            {k: sum(r["four_clause_steps_needing_a_birth"][k] for r in data) for k in FOUR_KINDS},
        "archive_matching_bond_and_box_counts": sum(r["laws_checked"][law]["matches"] for r in data),
    }


def census(args):
    begin = perf_counter()
    stages = json.loads((HERE / "growth_stages.json").read_text())
    archives = archived_counts()
    assert {(s["law"], s["census_id"]) for s in stages} == set(archives)
    selected = set(args.cases) if args.cases else None
    if selected:
        assert selected <= {s["census_id"] for s in stages}
    lib = kernel()
    rows = []
    rec_by_key = {}
    witnesses = {}
    for s in stages:
        cid = s["census_id"]
        if selected is not None and cid not in selected:
            continue
        signature = (cid, tuple(map(tuple, s["supports"])), s["start_knots"], tuple(s["last_birth_knots"]))
        if signature not in rec_by_key:
            stage_begin = perf_counter()
            row, examples = search(lib, s["supports"], s["start_knots"], s["last_birth_knots"])
            if examples:
                witnesses[f"{s['law']}_{cid}"] = examples
                if args.witnesses:
                    write_json(HERE / args.witnesses, witnesses)
                print("upper step on census entry", cid, list(examples), flush=True)
            row.update(census_id=cid, round=s["round"], seconds=round(perf_counter() - stage_begin, 4),
                       laws_checked={})
            rec_by_key[signature] = row
            rows.append(row)
        row = rec_by_key[signature]
        assert row["round"] == s["round"]
        archive = archives[s["law"], cid]
        row["laws_checked"][s["law"]] = {
            "archived_bonds": archive["bonds"], "archived_boxes": archive["boxes"],
            "matches": (archive["bonds"], archive["boxes"]) == (row["bonds"], row["boxes"]),
        }
    data = dict(
        census_ids=(sorted(selected) if selected is not None else "all newly closed"),
        summary={law: summarize(rows, law) for law in ("one_fewer", "arity_floor")},
        rows=rows, distinct_replays=len(rows), elapsed_seconds=round(perf_counter() - begin, 4),
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )
    write_json(HERE / args.output, data)
    if args.witnesses and witnesses:
        write_json(HERE / args.witnesses, witnesses)
    print(json.dumps(data["summary"]["arity_floor"], indent=2), flush=True)
    print("seconds", data["elapsed_seconds"], "peak KiB", data["peak_rss_kib"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", type=int)
    parser.add_argument("--output", required=True)
    parser.add_argument("--witnesses")
    census(parser.parse_args())

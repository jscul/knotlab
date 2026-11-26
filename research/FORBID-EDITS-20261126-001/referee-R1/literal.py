"""Replay a seeded sample from the census and extension with exact truth tables."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
from random import Random
import resource
from time import perf_counter

from growth import grow


STUDY = Path(__file__).resolve().parents[1]
SEED = 4213845
DIRECT_WIDTH = 20
WEIGHTINGS = "U", "S"
BYTE_VALUES = [tuple(i for i in range(8) if byte >> i & 1) for byte in range(256)]


def bits_of(supports):
    return tuple(sorted({d for support in supports for d in support}))


def assignments(mask):
    """The values of integers whose positions are set in this truth table."""
    for i, byte in enumerate(mask.to_bytes((mask.bit_length() + 7) // 8, "little")):
        for j in BYTE_VALUES[byte]:
            yield 8 * i + j


class TruthTable:
    def __init__(self, variables):
        width = len(variables)
        size = 1 << width
        self.all = (1 << size) - 1
        self.positions = {d: i for i, d in enumerate(variables)}
        self.ones = {}
        for d, i in self.positions.items():
            if i < 3:
                pattern = bytes(((0xAA, 0xCC, 0xF0)[i],)) * max(1, size // 8)
            else:
                run = 1 << (i - 3)
                pattern = (b"\x00" * run + b"\xff" * run) * (size // (16 * run))
            self.ones[d] = int.from_bytes(pattern, "little") & self.all

    def all_equal(self, support):
        all_zero = all_one = self.all
        for d in support:
            all_zero &= self.all ^ self.ones[d]
            all_one &= self.ones[d]
        return all_zero, all_one

    def allows(self, support, law):
        if law == "nae":
            zero, one = self.all_equal(support)
            return self.all ^ (zero | one)
        odd = 0
        for d in support:
            odd ^= self.ones[d]
        return self.all ^ odd

    def conjunction(self, supports, law):
        states = self.all
        for support in supports:
            states &= self.allows(support, law)
        return states

    def histogram(self, mask, variables):
        widths = tuple(self.positions[d] for d in variables)
        if mask.bit_count() <= 8 * (1 << len(widths)):
            return Counter(tuple(word >> i & 1 for i in widths) for word in assignments(mask))
        counts = Counter()

        def separate(rest, values, i):
            if not rest:
                return
            if i == len(variables):
                counts[values] = rest.bit_count()
                return
            one = rest & self.ones[variables[i]]
            separate(rest ^ one, values + (0,), i + 1)
            separate(one, values + (1,), i + 1)

        separate(mask, (), 0)
        return counts


def projected(dist, positions):
    result = Counter()
    for word, p in dist.items():
        result[tuple(word[i] for i in positions)] += p
    return result


def normalize(u_counts, s_counts, total, retained):
    uniform = {k: Fraction(v, total) for k, v in u_counts.items()}
    survivor_mass = Counter()
    for completion_count, counts in s_counts.items():
        for k, v in counts.items():
            survivor_mass[k] += Fraction(v, completion_count * retained)
    assert sum(uniform.values()) == sum(survivor_mass.values()) == 1
    return {"U": uniform, "S": survivor_mass}


def complete_tables(variables, old_width, constraints, law, observations):
    """Directly select each allowed complete assignment and count its readings."""
    all_words = TruthTable(variables)
    legal = all_words.conjunction(constraints, law)
    old_mask = (1 << old_width) - 1
    completion_counts = Counter(word & old_mask for word in assignments(legal))
    counts = {name: (Counter(), defaultdict(Counter)) for name in observations}
    all_positions = {
        name: tuple(all_words.positions[d] for d in wanted)
        for name, wanted in observations.items()
    }
    for word in assignments(legal):
        denominator = completion_counts[word & old_mask]
        for name, positions in all_positions.items():
            value = tuple(word >> i & 1 for i in positions)
            u_counts, s_counts = counts[name]
            u_counts[value] += 1
            s_counts[denominator][value] += 1
    total, retained = legal.bit_count(), len(completion_counts)
    tables = {
        name: normalize(u_counts, s_counts, total, retained)
        for name, (u_counts, s_counts) in counts.items()
    }
    return tables, total, set(completion_counts)


def completion_choices(table, birth, law):
    """Enumerate fresh assignments for each old input class of a single birth."""
    inputs, fresh = birth["inputs"], birth["fresh"]
    if law == "parity":
        even = table.allows(inputs, law)
        classes = ((even, (0,)), (table.all ^ even, (1,)))
    else:
        zero, one = table.all_equal(inputs)
        classes = ((zero, (0,)), (one, (1,)), (table.all ^ (zero | one), (0, 1)))
    options = []
    for old_mask, old_values in classes:
        allowed_fresh = []
        for values in product((0, 1), repeat=len(fresh)):
            all_values = values + old_values
            holds = sum(all_values) % 2 == 0 if law == "parity" else len(set(all_values)) > 1
            if holds:
                allowed_fresh.append(values)
        assert allowed_fresh
        if old_mask:
            options.append((old_mask, tuple(allowed_fresh)))
    return options


def completion_cells(states, choices, observed):
    """Group old assignments only when their fresh choices and counts agree."""
    conditions = []
    for i, birth_options in enumerate(choices):
        collapsed = defaultdict(int)
        for old_mask, possible in birth_options:
            key = (len(possible), possible if i in observed else ())
            collapsed[key] |= old_mask
        conditions.append(tuple(collapsed.items()))

    def visit(states, index, total, local):
        if index == len(conditions):
            yield states, total, local
            return
        for (count, choices), mask in conditions[index]:
            selected = states & mask
            if selected:
                yield from visit(
                    selected, index + 1, total * count, local + (choices,) if choices else local,
                )

    yield from visit(states, 0, 1, ())


def tables_by_birth(table, retained, positive, law, observations):
    """Enumerate the old truth table and each newborn knot's fresh truth table.

    Fresh distinctions are disjoint among newborn knots. Their independent
    choices have a Cartesian product. Count unobserved choices by its size.
    """
    options = [completion_choices(table, birth, law) for birth in positive]
    assert all(d in table.positions for b in positive for d in b["inputs"])
    fresh_names = [d for b in positive for d in b["fresh"]]
    assert len(fresh_names) == len(set(fresh_names)) and not set(fresh_names) & table.positions.keys()
    n_retained = retained.bit_count()
    tables = {}
    complete_count = None
    for name, variables in observations.items():
        old = tuple(d for d in variables if d in table.positions)
        fresh = tuple(d for d in variables if d not in table.positions)
        visible = []
        for i, b in enumerate(positive):
            if set(fresh) & set(b["fresh"]):
                visible.append(i)
        by_birth = old + tuple(d for i in visible for d in positive[i]["fresh"])
        assert len(by_birth) == len(variables) and set(by_birth) == set(variables)
        order = tuple(by_birth.index(d) for d in variables)
        u_counts = Counter()
        s_counts = defaultdict(Counter)
        total = 0
        for states, completions, local_choices in completion_cells(retained, options, set(visible)):
            n_local = prod(len(x) for x in local_choices)
            n_outside = completions // n_local
            old_values = table.histogram(states, old)
            total += states.bit_count() * completions
            for choices in product(*local_choices):
                suffix = tuple(d for birth in choices for d in birth)
                for word, count in old_values.items():
                    packed = word + suffix
                    value = tuple(packed[i] for i in order)
                    u_counts[value] += count * n_outside
                    s_counts[n_local][value] += count
        assert complete_count is None or complete_count == total
        complete_count = total
        tables[name] = normalize(u_counts, s_counts, total, n_retained)
    return tables, complete_count


def setting_inputs(base, new, readers, setting, kind):
    edits = [[] for _ in base]
    for i, (held, chosen) in enumerate(zip(readers, setting, strict=True)):
        if kind == "E2" or chosen:
            edits[held[chosen] if kind == "E2" else held[0]].append(new + i)
    edited = tuple(support + tuple(extra) for support, extra in zip(base, edits, strict=True))
    return edited, tuple(d for extra in edits for d in extra)


def meeting_pattern(birth):
    return birth["parents"], birth["inputs"], birth["f"]


def ordered_unique(values):
    return tuple(dict.fromkeys(values))


def setting_records(edited, readers, births, birth_sides):
    records = []
    for i, side in enumerate(readers):
        owned = [birth for birth, sides in zip(births, birth_sides, strict=True) if i in sides]
        held = ordered_unique(d for h in side for d in edited[h])
        fresh = tuple(d for b in owned for d in b["fresh"])
        complete = ordered_unique((*held, *(d for b in owned for d in b["inputs"]))) + fresh
        records.append({
            "births": tuple(meeting_pattern(b) for b in owned),
            "stored distinctions": held + fresh,
            "all distinctions": complete,
            "omitted inputs": tuple(d for d in complete if d not in held + fresh),
        })
    return records


def completed_setting(base, edited, extra, law, births, sides, readers, read_bits):
    old_labels = bits_of(edited)
    truth = TruthTable(old_labels)
    unedited = truth.conjunction(base, law)
    edited_alone = truth.conjunction(edited, law)
    kept = unedited & edited_alone
    intended_lift = unedited
    if law == "parity":
        for d in extra:
            intended_lift &= truth.all ^ truth.ones[d]
    assert intended_lift == kept

    zero = [(b, owners) for b, owners in zip(births, sides, strict=True) if b["f"] == 0]
    zero_masks = [truth.allows(b["inputs"], law) for b, _ in zero]
    retained = kept
    for allowed in zero_masks:
        retained &= allowed
    zero_details = []
    for i, (birth, owners) in enumerate(zero):
        violates = kept ^ (kept & zero_masks[i])
        without = violates
        for j, allowed in enumerate(zero_masks):
            if i != j:
                without &= allowed
        zero_details.append({
            "birth": meeting_pattern(birth),
            "readers": owners,
            "rejected by birth alone": violates.bit_count(),
            "restored upon removing birth": without.bit_count(),
        })

    records = setting_records(edited, readers, births, sides)
    result = {
        "retained": retained.bit_count(),
        "kept": kept.bit_count(),
        "unedited": unedited.bit_count() >> len(extra),
        "edited alone": edited_alone.bit_count(),
        "zero details": zero_details,
        "records": records,
    }
    if not retained:
        return result

    observations = {"readings": read_bits}
    observations.update({i: rec["all distinctions"] for i, rec in enumerate(records)})
    support = tuple(b["inputs"] + b["fresh"] for b in births)
    variables = bits_of(edited + support)
    result["distinctions"] = len(variables)
    if len(variables) <= DIRECT_WIDTH:
        tables, total, old_words = complete_tables(
            variables, len(old_labels), base + edited + support, law, observations,
        )
        assert all(d == e for d, e in zip(variables, old_labels))
        assert old_words == set(assignments(retained))
        result["enumeration"] = "whole"
    else:
        positive = [b for b in births if b["f"]]
        tables, total = tables_by_birth(truth, retained, positive, law, observations)
        result["enumeration"] = "by birth"
    result["grown states"] = total
    result["tables"] = tables
    return result


def score(tables, positions):
    if len(positions) == 2:
        correlations = [
            sum(p if word[positions[0]] == word[positions[1]] else -p for word, p in t.items())
            for t in tables.values()
        ]
        return max(
            sum(sign * e for sign, e in zip(signs, correlations, strict=True))
            for signs in product((-1, 1), repeat=4) if prod(signs) == -1
        )
    targets = {"000": 0, "011": 1, "101": 1, "110": 1}
    return max(
        sum(
            p for setting, target in targets.items()
            for word, p in tables[setting].items()
            if sum(word[positions[i]] ^ flips[2 * i + int(s)] for i, s in enumerate(setting)) % 2 == target
        ) / 4
        for flips in product((0, 1), repeat=6)
    )


def first_change(by_context, reader):
    for a, b in combinations(by_context, 2):
        if a[reader] == b[reader] and by_context[a] != by_context[b]:
            return a, b
    return None


def record_change(by_context, reader, weighting, *, complete):
    views = {}
    for key, stage in by_context.items():
        rec = stage["records"][reader]
        full_dist = stage["tables"][reader][weighting]
        bits = rec["all distinctions"] if complete else rec["stored distinctions"]
        positions = tuple(rec["all distinctions"].index(d) for d in bits)
        views[key] = rec["births"], projected(full_dist, positions)
    pair = first_change(views, reader)
    if pair is None:
        return None
    a, b = pair
    (a_births, a_dist), (b_births, b_dist) = views[a], views[b]
    if a_births != b_births:
        return {"settings": pair, "births": [a_births, b_births]}
    word = min(w for w in a_dist.keys() | b_dist.keys() if a_dist.get(w, 0) != b_dist.get(w, 0))
    return {
        "settings": pair,
        "record values": word,
        "probabilities": [str(a_dist.get(word, 0)), str(b_dist.get(word, 0))],
    }


def compare_weightings(contexts, kind, readers):
    k = len(readers)
    summary, detail = {}, {}
    for w in WEIGHTINGS:
        reads = {key: t["tables"]["readings"][w] for key, t in contexts.items()}
        scores = {"fixed old value": str(score(reads, tuple(range(k))))}
        if kind == "E2":
            scores["added value"] = str(score(reads, (2, 3)))
        read_changes = {}
        for label in ("fixed old value", "added value", "joint"):
            if kind != "E2" and label != "fixed old value":
                continue
            changes = []
            for i in range(k):
                positions = (i,) if label == "fixed old value" else (k + i,) if label == "added value" else (i, k + i)
                views = {key: projected(dist, positions) for key, dist in reads.items()}
                changes.append(first_change(views, i))
            read_changes[label] = changes
        stored_records = [record_change(contexts, i, w, complete=False) for i in range(k)]
        complete_records = [record_change(contexts, i, w, complete=True) for i in range(k)]
        summary[w] = {
            "scores": scores,
            "single unchanged": not any(read_changes.get("joint", read_changes["fixed old value"])),
            "record unchanged": not any(stored_records),
        }
        detail[w] = {
            "reading changes": read_changes,
            "stored record changes": stored_records,
            "complete record changes": complete_records,
            "readings": {key: {"".join(map(str, x)): str(p) for x, p in sorted(dist.items())}
                         for key, dist in reads.items()},
        }
    return summary, detail


def attribution(contexts, k):
    rejections = {s: t["retained"] < t["kept"] for s, t in contexts.items()}
    unique = {
        s: Counter(str(z["readers"][0]) if len(z["readers"]) == 1
                   else "shared" if z["readers"] else "middle"
                   for z in t["zero details"])
        for s, t in contexts.items()
    }
    archived, upon_removal = [], []
    for i in range(k):
        owned = {s: {z["birth"]: z["restored upon removing birth"] for z in t["zero details"] if i in z["readers"]}
                 for s, t in contexts.items()}
        changes, causal_changes = [], []
        for s, a in owned.items():
            if s[i] == "1":
                continue
            far_fixed = s[:i] + "1" + s[i + 1:]
            b = owned[far_fixed]
            if a.keys() != b.keys() and (rejections[s] or rejections[far_fixed]):
                changes.append((s, far_fixed))
            if any((a if term in a else b)[term] for term in a.keys() ^ b.keys()):
                causal_changes.append((s, far_fixed))
        archived.append(changes)
        upon_removal.append(causal_changes)
    flags = {
        "forbids somewhere": any(rejections.values()),
        "one-sided forbidding": any(
            rejections[s] and any(str(i) in unique[s] for i in range(k)) for s in contexts
        ),
        "two-sided forbidding": any(
            rejections[s] and all(str(i) in unique[s] for i in range(k)) for s in contexts
        ),
        "forbidding changes with own setting": [bool(x) for x in archived],
        "on every side": all(archived),
        "zero-fresh births": {s: dict(counts) for s, counts in unique.items()},
    }
    return flags, {"archived criterion": archived, "removing the changed birth restores states": upon_removal}


def check(row, *, shared=False):
    """Rebuild one archived placement. Return values and comparison evidence."""
    base = tuple(map(tuple, row["supports"]))
    readers = tuple(map(tuple, row["readers"]))
    kind, law, arm = row["kind of edit"], row["law"], row["arm"]
    new = max(bits_of(base)) + 1
    ownership = Counter(d for holder in base for d in holder)
    roles = {h: i for i, side in enumerate(readers) for h in side}
    assert len(roles) == sum(map(len, readers))
    assert all(not set(base[a]) & set(base[b]) for a, b in combinations(roles, 2) if roles[a] != roles[b])
    marks = tuple(next((d for d in base[side[0]] if ownership[d] == 1), None) for side in readers)
    read_bits = marks + (tuple(new + i for i in range(len(readers))) if kind == "E2" else ())
    contexts, extra_checks = {}, {}

    def report(replayed):
        for context in contexts.values():
            context.pop("tables", None)
        differences = {
            name: {"archived": row.get(name), "replayed": value}
            for name, value in replayed.items()
            if (name in row or name not in WEIGHTINGS) and row.get(name) != value
        }
        return {
            "start": row["start"],
            "readers": readers,
            "supports": base,
            "kind of edit": kind,
            "law": law,
            "arm": arm,
            "differences": differences,
            "replayed": replayed,
            "settings": contexts,
            "checks": extra_checks,
        }

    if None in marks:
        return report({"kind": "not read", "why": "a reader holder has no loose distinction to read"})
    any_shared = False
    for values in product((0, 1), repeat=len(readers)):
        setting = "".join(map(str, values))
        edited, extra = setting_inputs(base, new, readers, values, kind)
        status, births = grow(edited, law, arm)
        births = sorted(births, key=meeting_pattern)
        sides = [tuple(sorted({roles[h] for h in b["parents"] if h in roles})) for b in births]
        has_shared = any(len(s) > 1 for s in sides)
        any_shared |= has_shared
        if has_shared and not shared:
            extra_checks["first shared setting"] = setting
            return report({"kind": "shared birth"})
        result = completed_setting(base, edited, extra, law, births, sides, readers, read_bits)
        result["status"] = status
        result["middle births"] = tuple(meeting_pattern(b) for b, s in zip(births, sides, strict=True) if not s)
        contexts[setting] = result
        if not result["retained"]:
            return report({"kind": "no allowed state", "setting": list(values)})

    flags, attributions = attribution(contexts, len(readers))
    status = {s: t["status"] for s, t in contexts.items()}
    splits = len({(t["status"], t["middle births"]) for t in contexts.values()}) == 1
    scores, weight_details = compare_weightings(contexts, kind, readers)
    extra_checks.update({
        "local birth pattern changes": [
            first_change({s: t["records"][i]["births"] for s, t in contexts.items()}, i)
            for i in range(len(readers))
        ],
        "own-setting attribution": attributions,
        "weightings": weight_details,
    })
    return report({
        "kind": "shared birth, read" if any_shared else "read",
        "status": status,
        "splits": splits,
        "retained of old": {s: [t["retained"], t["kept"]] for s, t in contexts.items()},
        **flags,
        **scores,
    })


def archive_rows(path):
    with gzip.open(path, "rt") as handle:
        for line, raw in enumerate(handle, 1):
            yield line, json.loads(raw)


def stratum(source, row):
    kind = row["kind"]
    if kind == "read":
        statuses = set(row["status"].values())
        funding = "funded" if statuses == {"funded"} else "mixed" if "funded" in statuses else "unfunded"
        rejection = "none"
        if row["forbids somewhere"]:
            rejection = "own-setting flag" if any(row["forbidding changes with own setting"]) else "without own-setting flag"
        kind = (kind, funding, row["splits"], rejection)
    else:
        kind = (kind,)
    return (source, row["kind of edit"], row["law"], row["arm"], *kind)


def sample():
    random = Random(SEED)
    choices, counts = {}, Counter()
    for path in sorted((*STUDY.glob("tables5_*.jsonl.gz"), *STUDY.glob("xrun_*.jsonl.gz"))):
        source = "census" if path.name.startswith("tables5") else "extension"
        for line, row in archive_rows(path):
            key = stratum(source, row)
            counts[key] += 1
            priority = random.random()
            if key not in choices or priority < choices[key][0]:
                choices[key] = priority, path.name, line, row
    return [(key, counts[key], *choices[key][1:]) for key in sorted(choices)]


def pilot_subset(choices):
    out = []
    for source in ("census", "extension"):
        for edit in ("E1", "E2", "M1"):
            for law in ("parity", "nae"):
                group = [entry for entry in choices if entry[0][:3] == (source, edit, law) and entry[-1]["kind"] == "read"]
                out.append(max(group, key=lambda entry: (
                    "funded" in entry[-1]["status"].values(),
                    entry[-1]["forbids somewhere"],
                    len(bits_of(entry[-1]["supports"])),
                )))
    for kind in ("shared birth", "not read", "no allowed state"):
        entry = next((entry for entry in choices if entry[-1]["kind"] == kind), None)
        if entry is not None:
            out.append(entry)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    start = perf_counter()
    sampled = sample()
    selection_time = perf_counter() - start
    subset = pilot_subset(sampled) if args.pilot else sampled
    cases = []
    sys_time = perf_counter()
    for key, size, path, line, row in subset:
        case_start = perf_counter()
        result = check(row)
        result["seconds"] = perf_counter() - case_start
        result["source"] = {"archive": path, "line": line, "stratum": key, "stratum size": size}
        cases.append(result)
    summary = {
        "seed": SEED,
        "pilot": args.pilot,
        "whole truth table distinction limit": DIRECT_WIDTH,
        "archived rows": sum(x[1] for x in sampled),
        "sampled rows": len(sampled),
        "selection seconds": selection_time,
        "checking seconds": perf_counter() - sys_time,
        "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "checked rows": len(cases),
        "differences": sum(bool(case["differences"]) for case in cases),
        "settings checked": sum(len(case["settings"]) for case in cases),
        "settings by enumeration": dict(Counter(
            t["enumeration"] for case in cases for t in case["settings"].values() if "enumeration" in t
        )),
    }
    writer = gzip.open if args.output.suffix == ".gz" else open
    with writer(args.output, "wt") as stream:
        json.dump({"summary": summary, "cases": cases}, stream, indent=2)
        stream.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

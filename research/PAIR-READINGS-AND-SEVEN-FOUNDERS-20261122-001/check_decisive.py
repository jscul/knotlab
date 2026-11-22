"""Independently reconstruct the named table and check the smallest physical closure."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC = Path(__file__).resolve().parent.name
OLD = "NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A"
OLD_DATA = ROOT / "artifacts" / OLD / (OLD + "-E001_newest_knots")
NEW_DATA = ROOT / "artifacts" / (EPIC + "B") / (EPIC + "B-E001_seven_founders")


def uniform_pairs(holdings, width):
    """Count through intersections of monochromatic holder events on the full word."""
    pairs = list(combinations(range(width), 2))
    sign_sums = dict.fromkeys(pairs, 0)
    total = 0
    for chosen in range(1 << len(holdings)):
        same = [{name} for name in range(width)]
        for i, row in enumerate(holdings):
            if chosen >> i & 1:
                merged = set().union(*(same[x] for x in row))
                for name in merged:
                    same[name] = merged
        classes = len({min(members) for members in same})
        contribution = (-1) ** chosen.bit_count() * (1 << classes)
        total += contribution
        for a, b in pairs:
            if b in same[a]:
                sign_sums[a, b] += contribution
    return total, {k: Fraction(s, total) for k, s in sign_sums.items()}


def pair_certificate():
    record = json.loads((OLD_DATA / "reference.json").read_text())
    stored = list(map(Fraction, json.loads((OLD_DATA / "target_uniform.json").read_text())))
    width = 31
    holdings = record["stage"]
    total, corr = uniform_pairs(holdings, width)
    pairs = list(combinations(range(width), 2))
    assert [(1 - corr[e]) / 2 for e in pairs] == stored
    assert total == 601181310 and record["next_count"] == len(record["profile"]) == 7
    assert holdings[-1] == [8, 29, 30]
    old_total, old = uniform_pairs(holdings[:-1], 29)
    assert old_total == 200393770 and all(corr[e] == c for e, c in old.items())
    old_occurrences = Counter(x for row in holdings[:-1] for x in row)
    old_loose = sorted(x for x, count in old_occurrences.items() if count == 1)
    assert old_loose == [8, *range(17, 29)]

    def moment(i, j):
        return Fraction(1) if i == j else old[tuple(sorted((i, j)))]

    # Complement symmetry gives the probability that a triple is all equal.
    triples = [(1 + moment(i, j) + moment(j, k) + moment(i, k)) / 4
               for i, j, k in combinations(range(29), 3)]
    assert min(triples) > 0
    twins = {(i, j) for i, j in combinations(range(29), 2)
             if all(moment(i, z) == moment(j, z) for z in range(29) if z not in (i, j))}
    expected_groups = [(1, 2), (17, 18), (19, 20), (21, 22), (23, 24, 25), (26, 27, 28)]
    assert twins == {pair for group in expected_groups for pair in combinations(group, 2)}
    t = 23
    shared = moment(t, 24)
    assert all(moment(t, z) == shared for z in (5, 13, 25))
    assert all(14 * moment(t, z) + moment(5, z) + moment(13, z) == 0
               for z in range(29) if z not in (23, 24, 25))
    return dict(words=total, checked_named_pairs=len(pairs), prior_words=old_total,
                actual_loose_after_erasing_unary=old_loose, actual_next_births=record["profile"],
                minimum_equal_triple_probability=str(min(triples)),
                exterior_row_classes=expected_groups, shared_minimum=str(shared),
                cancelled_exterior_moments=26)


def local_sign_checks():
    """Exercise the sign argument for distinct second holders and for a common one."""
    # The means are constants or strictly between them. Three test lengths
    # exercise both endpoints, all mixed words and common assigned signs.
    words = [w for n in (2, 3, 4) for w in product((-1, 1), repeat=n)]
    strict = zero = 0
    for left, right in product(words, repeat=2):
        diff = Fraction(sum(left), len(left)) - Fraction(sum(right), len(right))
        total = sum(2 * x * diff for x in (-1, 1)
                    if len(set(left + (x,))) > 1 and len(set(right + (-x,))) > 1)
        assert total <= 0
        if total < 0:
            strict += 1
        else:
            zero += 1
    # When the three siblings share their other holder too, a removed
    # constant word pushes the twin-versus-companion difference in one sign.
    for outer in product((-1, 1), repeat=2):
        for sibling_sign in (-1, 1):
            if all(x == sibling_sign for x in outer):
                continue
            loss = [1 - sibling_sign * x for x in outer]
            assert min(loss) >= 0 and sum(loss) > 0
    return dict(nonpositive_contexts=strict + zero, strictly_negative=strict,
                zero_contribution=zero)


@cache
def connected_named(n, meetings):
    """Subtract the proper connected component of the first named founder."""
    if meetings < 0 or meetings > comb(n, 2):
        return 0
    count = comb(comb(n, 2), meetings)
    for k in range(1, n):
        rest = comb(n - k, 2)
        for m in range(min(comb(k, 2), meetings) + 1):
            if meetings - m <= rest:
                count -= comb(n - 1, k - 1) * connected_named(k, m) * comb(rest, meetings - m)
    return count


def closure_certificate():
    controls = json.loads((NEW_DATA / "physical_controls.json").read_text())
    totals = json.loads((NEW_DATA / "census_totals.json").read_text())
    census = {}
    for law, entries in totals["outcomes"].items():
        tally = Counter()
        for row in entries:
            tally[row["status"]] += row["orbit"]
        census[law] = dict(tally)
    parity = controls["seven_examples"]["closure_1"]["laws"]["parity"]
    other = controls["seven_examples"]["closure_1"]["laws"]["nae"]
    current = [tuple(row) for row in parity["source"]]
    seen = Counter(d for row in current for d in row)
    assert len(current) == 7 and sum(n == 2 for n in seen.values()) == 8
    cohort_records = []
    for cut in parity["history"]:
        assert cut["before"] == [list(row) for row in current]
        loose = {d for d, count in seen.items() if count == 1}
        spent = []
        rows = []
        for birth in cut["births"]:
            assert len(birth["parents"]) == len(birth["paid"])
            assert all(d in current[p] for p, d in zip(birth["parents"], birth["paid"], strict=True))
            spent.extend(birth["paid"])
            rows.append(tuple(birth["paid"] + birth["fresh"]))
        assert set(spent) == loose and len(spent) == len(loose)
        current.extend(rows)
        seen.update(d for row in rows for d in row)
        cohort_records.append(dict(parents=[v["parents"] for v in cut["births"]],
                                   paid=[v["paid"] for v in cut["births"]],
                                   fresh=[v["fresh"] for v in cut["births"]]))
    assert len(current) == 11 and set(seen.values()) == {2}
    width = len(seen)
    masks = [sum(1 << x for x in row) for row in current]
    before = [w for w in range(1 << width)
              if all((w & m).bit_count() % 2 == 0 for m in masks[:-1])]
    even = [w for w in before if (w & masks[-1]).bit_count() % 2 == 0]
    ending = sorted(current[-1])
    projected = {tuple((w >> i) & 1 for i in ending) for w in even}
    assert before == even and len(even) == 256 and len(projected) == 4 and len(ending) == 3
    assert len(other["history"][1]["births"][0]["fresh"]) == 1
    labelled = connected_named(7, 8)
    assert labelled == 156555 and labelled * 128 == totals["denominators"]["labelled_decorated"]
    return dict(connected_named_meeting_sets=labelled, decorated_named_starts=labelled * 128,
                census=census, minimal_source=current[:7], cohort_records=cohort_records,
                last_projected_words=sorted(projected), words_before=len(before),
                words_after=len(even), sign_reversed=len(before) - len(even),
                nae_fresh_on_same_birth=other["history"][1]["births"][0]["fresh"])


if __name__ == "__main__":
    print(json.dumps(dict(uniform_table=pair_certificate(), local_signs=local_sign_checks(),
                          seven_founders=closure_certificate()),
                     indent=2, sort_keys=True))

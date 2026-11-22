"""Independent physical and exact-law checks for the successor receipts."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PRIOR = "HIDDEN-SENDER-MARKS-20261122-001A"
OLD = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_hidden_sends")
INPUTS = {
    DATA / "alternate.json.gz": "e9fc4765288886313d46c596ee208e62d6f483d8ffdba842ec3833c3c5e9e0c2",
    DATA / "holders.json": "eca4aaf5d5d9d3e3397cd15ef080e9a5babc14bf95f6bdb4d52fdd48d48c1fb4",
    DATA / "joint.json.gz": "c0a4a6d4128d09858814b79034f8a8dbdc70c1f675d8e8f4a0eae2296505a775",
    DATA / "readouts.json.gz": "a544ba337dd4596b813157b64e4fdbf827a223a0fcc40e2aa05f3197eb4e89fc",
    DATA / "witnesses.json.gz": "6c6057be706e82e9c117a0288930845dc76284c722e9bf92a8163d58d27e2b01",
    OLD / "growth.json.gz": "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    OLD / "supports.json.gz": "35d55ff7594316542c0ee003ea4c0de1c82eda207c66b82a54961b1befccbf80",
}
LAWS = ("parity", "nae")
ROUTES = ("intact", "interrupted", "sham")
HOLDERS = (631, 633, 634)
R_FRESH = (1754, 1755, 1756)
SOURCE = (510, 563)
READS = ("fresh", "anonymous", "calibrated")
TARGETS = ("W", "paid_bit", "early_action", "late_request", "late_moved", "bit_and_late", "W_and_late")


def mask(names):
    return sum(1 << d for d in names)


def read(word, names):
    return "".join(str(word >> d & 1) for d in names)


def binary(width):
    return map("".join, product("01", repeat=width))


def legal(law, size, count):
    return count % 2 == 0 if law == "parity" else 0 < count < size


def reads(wi, u, own):
    return (own, "".join(sorted(wi + u)) + "/" + own, wi + u + "/" + own)


class Board:
    def __init__(self, growth, course, law, route):
        self.law = law
        self.stars = list(growth["original_stars"])
        self.old_domain = self.domain()
        self.births = {}
        for cut in growth["cases"][route][law]["cuts"]:
            self.append(cut)
        self.third = tuple((mask(row), len(row)) for row in self.stars)
        self.third_domain = self.domain()
        self.third_stars = list(self.stars)
        self.append(course["fourth"])
        self.fourth = tuple((mask(row), len(row)) for row in self.stars)
        self.fourth_domain = self.domain()
        assert len(self.third) == 647 and len(self.fourth) == 1611

    def domain(self):
        return mask({d for row in self.stars for d in row})

    def append(self, status):
        assert status["status"] == "extend"
        owners = defaultdict(list)
        for holder, row in enumerate(self.stars):
            assert len(row) == len(set(row))
            for d in row:
                owners[d].append(holder)
        supply = {d for d, present in owners.items() if len(present) == 1}
        newly_issued = set()
        for birth in status["births"]:
            assert birth["holder"] == len(self.stars)
            assert birth["fresh_names"] and birth["grant"] == len(birth["fresh_names"])
            assert len(birth["parents"]) == len(set(birth["parents"]))
            for d, payer in zip(birth["consumed_names"], birth["parents"], strict=True):
                assert owners[d] == [payer]
                supply.remove(d)
            for d in birth["fresh_names"]:
                assert d not in owners and d not in newly_issued
                newly_issued.add(d)
            self.births[birth["holder"]] = birth
            self.stars.append(birth["consumed_names"] + birth["fresh_names"])
        assert not supply

    def legal(self, word, rules):
        return all(legal(self.law, n, (word & m).bit_count()) for m, n in rules)

    def check_clock(self, h, reported):
        old = self.births[h]["consumed_names"]
        fresh = self.births[h]["fresh_names"]
        assert old == reported["old_inputs"] and fresh == reported["own_new"]
        assert self.births[h]["parents"] == reported["all_parents"]
        others = lambda names, stars: [[i for i, row in enumerate(stars) if i != h and name in row] for name in names]
        assert others(old, self.third_stars) == others(old, self.stars) == [[p] for p in reported["all_parents"]]
        assert len(set(reported["all_parents"])) == 2
        assert others(fresh, self.third_stars) == [[] for _ in fresh]
        assert others(fresh, self.stars) == [[p] for p in reported["fourth_recipients"]]
        assert len(set(reported["fourth_recipients"])) == len(fresh)
        assert reported["own_clock"] == [[None] * len(fresh), list(range(len(fresh)))]


def completions(law, paid, width, observed="", also=None):
    """Count whole bank choices compatible with one fixed slot restriction."""
    free = width - len(observed)
    total = len(paid) + width
    assert free >= 0
    result = 0
    for ones in range(free + 1):
        fresh_ones = ones + observed.count("1")
        if legal(law, total, paid.count("1") + fresh_ones):
            if also is None or legal(law, total, also.count("1") + fresh_ones):
                result += comb(free, ones)
    return result


def independent_joint(board, holder, old, route):
    """Eliminate each contributing first holder by exact pin counts."""
    law, births = board.law, board.births
    h, r = births[holder], births[294]
    ix = h["parents"].index(294)
    pos = HOLDERS.index(holder)
    q = births[h["parents"][1 - ix]]
    u_name = h["consumed_names"][1 - ix]
    assert h["consumed_names"][ix] == R_FRESH[pos]
    assert u_name in q["fresh_names"]
    need = defaultdict(set)
    for child in (r, q):
        for payer, d in zip(child["parents"], child["consumed_names"], strict=True):
            assert d in births[payer]["fresh_names"]
            need[payer].add(d)
    affected = {163, 164 if route == "interrupted" else 162}
    for carrier in affected:
        need.setdefault(carrier, set())
    rankings = []
    for payer, used_names in sorted(need.items()):
        row = births[payer]
        before = read(old, row["consumed_names"])
        changed_inputs = set(row["consumed_names"]) & set(SOURCE)
        assert len(changed_inputs) == int(payer in affected)
        after = read(old ^ mask(SOURCE), row["consumed_names"]) if payer in affected else before
        width = row["grant"]
        mass = completions(law, before, width)
        ordered_names = sorted(used_names)
        options = []
        for shown in binary(len(ordered_names)):
            denominator = completions(law, before, width, shown)
            accepts = completions(law, before, width, shown, also=after)
            pins = dict(zip(ordered_names, shown, strict=True))
            for status, count in ((True, accepts), (False, denominator - accepts)):
                if count:
                    options.append((status, pins, Fraction(count, mass)))
        assert sum(option[2] for option in options) == 1
        rankings.append(options)
    result = Counter()
    for allocations in product(*rankings):
        old_values = {}
        joint_weight = Fraction(1)
        positive = True
        for accepted, pins, weight in allocations:
            assert not set(old_values).intersection(pins)
            old_values.update(pins)
            joint_weight *= weight
            positive &= accepted
        r_paid, q_paid = ("".join(old_values[d] for d in row["consumed_names"]) for row in (r, q))
        q_count = completions(law, q_paid, q["grant"])
        for w in binary(r["grant"]):
            if not legal(law, len(r_paid) + len(w), (r_paid + w).count("1")):
                continue
            r_count = completions(law, r_paid, r["grant"])
            for u in "01":
                q_accept = completions(law, q_paid, q["grant"], u)
                if not q_accept:
                    continue
                h_paid = w[pos] + u
                h_count = completions(law, h_paid, h["grant"])
                for word in binary(h["grant"]):
                    if legal(law, len(h_paid) + len(word), (h_paid + word).count("1")):
                        result[positive, w, u, word] += joint_weight * Fraction(q_accept, q_count * r_count * h_count)
    assert sum(result.values()) == 1
    return result


def summary(table):
    prior = Counter()
    for row in table.values():
        prior.update(row)
    total = sum(prior.values())
    sure = [row for row in table.values() if len(row) == 1]
    return {"available": True, "records": len(table), "certain_records": len(sure),
            "distinct_truth_per_record": {str(k): n for k, n in Counter(map(len, table.values())).items()},
            "certain_mass": str(sum(sum(row.values()) for row in sure) / total),
            "best_accuracy": str(sum(max(row.values()) for row in table.values()) / total),
            "best_prior": str(max(prior.values()) / total), "mass": str(total),
            "certainty_all": len(sure) == len(table)}


def compare_readouts(pairs, pos, readouts, key, mode):
    overall = {(view, target): defaultdict(Counter) for view, target in product(READS, TARGETS)}
    conditioned = defaultdict(lambda: {(view, target): defaultdict(Counter)
                                       for view, target in product(READS, ("W", "paid_bit"))})
    for early, distribution in enumerate(pairs):
        for (admitted, w, u, own), probability in distribution.items():
            wi = w[pos]
            for request in (0, 1):
                moved = mode == "pointwise" and request == 1 and admitted
                status = "I" if not request else ("M" if moved else "U")
                group = f"{early}-{request}-{status}"
                action = "M" if moved else "no-move"
                truths = (w, wi, str(early), str(request), action, wi + "/" + action, w + "/" + action)
                for view, observation in zip(READS, reads(wi, u, own), strict=True):
                    for target, answer in zip(TARGETS, truths, strict=True):
                        overall[view, target][observation][answer] += probability / 4
                    conditioned[group][view, "W"][observation][w] += probability / 4
                    conditioned[group][view, "paid_bit"][observation][wi] += probability / 4
    expected = {view: {target: summary(overall[view, target]) for target in TARGETS} for view in READS}
    assert expected == readouts["overall"][key]
    assert not expected["anonymous"]["W"]["certain_records"]
    for view in READS:
        assert not expected[view]["W"]["certain_records"]
        assert expected[view]["late_request"]["best_accuracy"] == "1/2"
    sub = {group: {view: {target: summary(table[view, target]) for target in ("W", "paid_bit")} for view in READS}
           for group, table in conditioned.items()}
    assert sub == readouts["by_early_late_request_status"][key]
    supports = {group: {view: {obs: sorted(truth) for obs, truth in table[view, "W"].items()} for view in READS}
                for group, table in conditioned.items()}
    assert supports == readouts["whole_W_support_given_request_and_status"][key]
    return expected


def actual_trace(board, entry, old, holder, pos):
    pre, idle, attempt = (int(entry[k], 16) for k in ("third_before_late", "after_idle_finish", "after_pointwise_T_finish"))
    assert pre & ~board.third_domain == 0 and pre & board.old_domain == old
    assert int(entry["background"], 16) == old and board.legal(pre, board.third)
    assert idle & board.third_domain == pre and idle & ~board.fourth_domain == 0
    assert board.legal(idle, board.fourth)
    candidate = pre ^ mask(SOURCE)
    allowed = board.legal(candidate, board.third)
    assert allowed == entry["late_pointwise_admitted"]
    assert attempt == (idle ^ mask(SOURCE) if allowed else idle)
    assert board.legal(attempt, board.fourth)
    h = board.births[holder]
    actual = read(pre, board.stars[holder])
    assert actual == entry["H_actual"] == read(idle, board.stars[holder]) == read(attempt, board.stars[holder])
    w = read(pre, R_FRESH)
    assert w == entry["W"] and w[pos] == entry["r_inheritance"]
    here = h["parents"].index(294)
    assert read(pre, [h["consumed_names"][1 - here]]) == entry["coparent_bit"]
    assert read(pre, h["fresh_names"]) == entry["H_fresh"]
    return (allowed, w, entry["coparent_bit"], entry["H_fresh"])


def check_traces(board, raw, old, holder, pos, joint):
    tallies = Counter()
    for trial in raw:
        a = actual_trace(board, trial["first"], old, holder, pos)
        assert a in joint
        b = actual_trace(board, trial["other"], old, holder, pos) if trial["other"] is not None else None
        if b:
            assert b in joint and a[0] == b[0] and a[1] != b[1]
            e1, e2 = (reads(val[1][pos], val[2], val[3]) for val in (a, b))
        kind = trial["kind"]
        if kind == "same_preoffer_skip_or_attempt":
            assert b is None
        elif kind == "same_entire_oriented_H_distinct_W":
            assert b and e1[2] == e2[2]
        elif kind == "same_anonymous_H_opposite_paid_bit":
            assert b and e1[1] == e2[1] and a[1][pos] != b[1][pos]
        elif kind == "equal_incoming_tracks_witness":
            assert b is None and a[1][pos] == a[2]
        else:
            raise ValueError(f"Unexpected witness class {kind}")
        tallies[kind] += 1
    return tallies


def knot_projection(law, paid_pairs, width, names):
    assert paid_pairs == set(binary(2))
    assert len(names) == width + 2 and len(set(names)) == len(names)
    table = {p + rest for p, rest in product(paid_pairs, binary(width))
             if legal(law, len(names), (p + rest).count("1"))}
    proper = [len({word[:i] + word[i + 1:] for word in table}) for i in range(len(names))]
    assert 0 < len(table) < 1 << len(names) and proper == [1 << (len(names) - 1)] * len(names)
    return {"actual_names": names, "full_allowed_words": len(table), "one_mark_omissions": proper}


def alternate_witnesses(alt, board, old):
    selected = alt["later_source_enrollment"]["selected"]
    a = alt["later_source_controls"][board.law]
    g, k, h = (selected[x] for x in ("G", "K", "H"))
    assert (g, k, h) == (1595, 632, 631)
    hp, q, spare, xi, other = (selected[x] for x in ("paid_h", "paid_q", "spare_q", "old_R_name", "other_H_input"))
    assert [i for i, row in enumerate(board.third_stars) if q in row] == [k]
    assert [i for i, row in enumerate(board.third_stars) if spare in row] == [k]
    assert [i for i, row in enumerate(board.third_stars) if hp in row] == [h]
    assert board.births[g] == a["G_actual_birth"]
    assert board.births[g]["consumed_names"] == [hp, q] and xi not in board.stars[g]
    assert a["G_observation_end"] == "finish" and len(a["fifth"]["births"]) == 2782
    board.append(a["fifth"])
    final_rows = tuple((mask(row), len(row)) for row in board.stars)
    final_domain = board.domain()
    assert a["G_own_finish"]["coholder_samples"] == [[None, None, None], [0, 1, 2]]
    pairs = set()
    count = Counter()
    for mode, scope in a["modes"].items():
        actual = defaultdict(set)
        for witness in scope["whole_paired_examples"]:
            common = int(witness["common_cut_three_state"], 16)
            word, h_value = witness["W"], witness["h"]
            assert common & ~board.third_domain == 0 and common & board.old_domain == old
            assert board.legal(common, board.third) and read(common, R_FRESH) == word
            assert read(common, (q, spare)) == "01" and read(common, (hp,)) == str(h_value)
            if mode == "calibrated":
                locked = [other] + [d for d in board.births[h]["fresh_names"] if d != hp]
                assert read(common, locked) == "0" * len(locked)
            assert h_value not in actual[word]
            actual[word].add(h_value)
            for arm, q_value in (("I", 0), ("T", 1)):
                three, four, five = (int(witness["arms"][arm][kind], 16)
                                     for kind in ("cut_three_after", "cut_four_after", "cut_five_after"))
                assert three == (common ^ mask((q, spare)) if q_value else common)
                assert board.legal(three, board.third) and board.legal(four, board.fourth)
                assert board.legal(five, final_rows) and five & ~final_domain == 0
                assert four & board.third_domain == three and five & board.fourth_domain == four
                if mode == "natural":
                    pairs.add(read(four, (hp, q)))
                count[mode] += 1
        assert {w: sorted(s) for w, s in actual.items()} == scope["paid_h_by_full_W"]
        expected = {w: ([0, 1] if mode == "natural" or (board.law == "nae" and w[0] == "1")
                        else [int(w[0])] if board.law == "parity" else [1]) for w in binary(3)}
        assert {w: sorted(s) for w, s in actual.items()} == expected
    return dict(count), knot_projection(board.law, pairs, board.births[g]["grant"], board.stars[g])


def audit():
    raw = {path: path.read_bytes() for path in INPUTS}
    assert {path: sha256(word).hexdigest() for path, word in raw.items()} == INPUTS
    blobs = {path.name: json.loads(gzip.decompress(word) if path.suffix == ".gz" else word)
             for path, word in raw.items()}
    previous = {(x["law"], x["route"]): x["weighted"] for x in blobs["supports.json.gz"]["projections"]
                if x["target"] == "R" and x["side"] == "00"}
    growth, alt, joint = (blobs[key] for key in ("growth.json.gz", "alternate.json.gz", "joint.json.gz"))
    old_words = {law: mask(d for d, bit in zip(growth["original_name_order"], growth["common_original_words"][law], strict=True)
                           if bit == "1") for law in LAWS}
    factors = 0
    signs = Counter()
    projections, controls, sample_rates = {}, {}, {}
    for law, route in product(LAWS, ROUTES):
        board = Board(growth, alt["courses"][law][route], law, route)
        local = blobs["holders.json"][f"{law}-{route}"]
        for pos, holder in enumerate(HOLDERS):
            board.check_clock(holder, local[pos])
            key = f"{law}-{route}-{holder}"
            pair = []
            old_pairs = set()
            for early in (0, 1):
                old = old_words[law] ^ (mask(SOURCE) if early else 0)
                results = independent_joint(board, holder, old, route)
                factor = f"{key}-{early}"
                raw_rows = joint["factors"][factor]
                stored = {(x["pointwise_ok"], x["W"], x["u"], x["H_fresh"]): Fraction(x["mass"]) for x in raw_rows}
                assert results == stored and len(stored) == len(raw_rows)
                r = Counter()
                for (_, w, u, _), mass in results.items():
                    old_pairs.add(w[pos] + u)
                    r[w] += mass
                assert r == {w: Fraction(p) for w, p in previous[law, route][("idle", "swap")[early]].items()}
                signs.update(check_traces(board, blobs["witnesses.json.gz"]["traces"][factor], old, holder, pos, results))
                pair.append(results)
                factors += 1
            projections[key] = knot_projection(law, old_pairs, board.births[holder]["grant"], board.stars[holder])
            for mode in ("structural", "pointwise"):
                held = compare_readouts(pair, pos, blobs["readouts.json.gz"], key + "-" + mode, mode)
                if holder == 631 and mode == "pointwise":
                    sample_rates[f"{law}-{route}"] = {target: held["anonymous"][target]["best_accuracy"]
                                                    for target in ("early_action", "paid_bit", "late_moved")}
        if route == "intact":
            check, projections[f"{law}-G"] = alternate_witnesses(alt, board, old_words[law])
            controls[law] = check
    assert factors == len(joint["factors"]) == len(blobs["witnesses.json.gz"]["traces"]) == 36
    return {"pass": True, "validation_class": "V1 same-task independent calculation",
            "inputs_sha256": {str(path.relative_to(ROOT)): digest for path, digest in INPUTS.items()},
            "recalculated_conditional_factors": factors, "replayed_main_trace_classes": dict(signs),
            "alternate_full_physical_arms_checked": controls,
            "actual_local_K1_K2_K3": projections, "anonymous_H0_selected_rates": sample_rates}


if __name__ == "__main__":
    path = DATA / "audit.json"
    path.write_text(json.dumps(audit(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(sha256(path.read_bytes()).hexdigest(), path)

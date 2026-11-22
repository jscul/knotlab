"""Independent physical replay of the reached sibling source and guarded keeper."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
from random import Random
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAST = ROOT / "research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001B"
ROUTES = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py"
LAWS = ("parity", "nae")
ARMS = ("ordinary", "one_fewer", "arity_floor")
U = (0, 1, 2, 3)
FOCAL = (4, 5, 6)
ROWS = ((7, 8, 9), (10, 11, 12), (13, 14, 15))
OLD = (U, (0, *FOCAL), *((i, *row) for i, row in enumerate(ROWS, 1)))
A, B, C, D, E, F, H_PRIVATE, K_PRIVATE, L_PRIVATE = range(16, 25)
ABC, DEF = (A, B, C), (D, E, F)
TQ = tuple(tuple((25 + 6 * i + 2 * j, 26 + 6 * i + 2 * j) for j in range(3)) for i in range(3))
SCRATCH = tuple(d for bank in TQ for pair in bank for d in pair)
H, K, L = 5, 6, 7
READY, ZERO, ONE = (1, 1, 0), (1, 0, 1), (0, 1, 1)
OLD_SCOPE = (1 << 16) - 1
FOCAL_SCOPE = sum(1 << d for d in FOCAL)
SLACK_SCOPE = 1 << H_PRIVATE


@cache
def precedent():
    spec = spec_from_file_location("b302_b256_native", PAST / "native.py")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def mask(names):
    return sum(1 << d for d in names)


def values(word, names):
    return tuple((word >> d) & 1 for d in names)


def encode(names, bits):
    return sum(u << d for d, u in zip(names, bits, strict=True))


def allowed(word, support, law):
    part = word & support
    return part.bit_count() % 2 == 0 if law == "parity" else part not in (0, support)


@cache
def old_words(law):
    supports = tuple(map(mask, OLD))
    words = tuple(word for word in range(1 << 16) if all(allowed(word, row, law) for row in supports))
    assert len(words) == (8 * 4 ** 4 if law == "parity" else 14 * 7 ** 4)
    archived = json.loads(gzip.decompress((PAST / "native.json.gz").read_bytes()))
    growth = archived["cases"]["isolated_four"]["laws"][law]["histories"]["ordinary"]["cuts"][0]
    assert tuple(map(tuple, growth["stars_after"])) == OLD
    assert {d for b in growth["births"] for d in b["fresh_names"]} == set(range(4, 16))
    return words


@cache
def apparatus(kind):
    if kind == "bare":
        return OLD
    omitted = {row[2] for row in ROWS} if kind == "restricted" else {
        int(kind.split("_")[1])} if kind.startswith("omit_") else set()
    exterior = tuple(d for row in ROWS for d in row if d not in omitted)
    return OLD + (exterior + ABC + (H_PRIVATE,) + SCRATCH,
                  ABC + DEF + (K_PRIVATE,), DEF + (L_PRIVATE,))


def legal_solver(stars, law):
    """Auxiliary SAT variables are verification only and name no physical place."""
    solver = Minisat22()
    aux = max(d for row in stars for d in row) + 2
    for row in stars:
        lits = [d + 1 for d in row]
        if law == "nae":
            solver.add_clause(lits)
            solver.add_clause([-d for d in lits])
            continue
        left = lits[0]
        for right in lits[1:]:
            out = aux
            aux += 1
            solver.add_clause([-left, -right, -out])
            solver.add_clause([left, right, -out])
            solver.add_clause([-left, right, out])
            solver.add_clause([left, -right, out])
            left = out
        solver.add_clause([-left])
    return solver


def pins(word, scope):
    return [d + 1 if word & (1 << d) else -d - 1 for d in scope]


def words_on(solver, scope):
    return tuple(bits for bits in product((0, 1), repeat=len(scope)) if solver.solve(
        assumptions=[d + 1 if value else -d - 1 for d, value in zip(scope, bits, strict=True)]))


def ready(old, stars, law, supplied_q=False):
    word = old | encode(ABC, READY) | encode(DEF, READY) | mask(bank[j][0] for bank in TQ for j in range(3))
    if supplied_q and old & 1:
        word ^= mask(TQ[0][2])
    if law == "parity" and not allowed(word, mask(stars[H]), law):
        word |= SLACK_SCOPE
    assert all(allowed(word, mask(star), law) for star in stars)
    return word


@cache
def auxiliary_count(exterior_has_zero, exterior_has_one, law):
    if law == "parity":
        return 1 << 24
    total = 0
    for a, d in product(range(8), repeat=2):
        h = (1 << 19) - int(a == 0 and not exterior_has_one) - int(a == 7 and not exterior_has_zero)
        k = 2 - int(a == d and a in (0, 7))
        l = 2 - int(d in (0, 7))
        total += h * k * l
    return total


def projected_apparatus(kind, law):
    stars = apparatus(kind)
    prior = precedent()
    owners, graph, loose = prior.incidence(stars)
    assert len(owners) == 43
    assert all(len(owners[d]) == 1 and owners[d] == [1] for d in FOCAL)
    assert all(len(owners[d]) == 2 for d in U)
    assert all(graph.has_edge(*pair) for pair in ((H, K), (K, L)))
    exterior = tuple(d for d in stars[H] if d < 16)
    old = old_words(law)
    by_scope = {}
    with legal_solver(stars, law) as solv:
        assert all(solv.solve(assumptions=pins(word, U + FOCAL + tuple(d for row in ROWS for d in row))) for word in old)
        for k, scope in enumerate(stars):
            if k == H:
                continue
            words = words_on(solv, scope)
            expected = tuple(bits for bits in product((0, 1), repeat=len(scope))
                             if allowed(encode(scope, bits), mask(scope), law))
            assert words == expected
            assert prior.canonical_local(len(scope), law) == len(words)
            by_scope[k] = {"names": scope, "projection": words, "K1_K2_K3": True, "number": len(words)}

        boundary = exterior + ABC
        assert len(words_on(solv, boundary)) == 1 << len(boundary)
        assert all(owners[d] == [H] for d in (H_PRIVATE, *SCRATCH))
        width = len(stars[H])
        by_scope[H] = {"names": stars[H], "projection": f"complete {law} relation",
                       "K1_K2_K3": True, "number": (1 << (width - 1)) if law == "parity" else (1 << width) - 2,
                       "full_shared_boundary": boundary, "all_shared_boundary_words_extend": 1 << len(boundary),
                       "independent_private_names": (H_PRIVATE, *SCRATCH)}

    prices = Counter()
    slack = Counter()
    ext = mask(exterior)
    for word in old:
        r = ready(word, stars, law)
        prices["ready"] += 1
        prices["lawful"] += auxiliary_count((word & ext) != ext, bool(word & ext), law)
        h = int(bool(r & SLACK_SCOPE))
        slack[word & 1, h] += 1
        if law == "parity" and kind == "full":
            assert h == 1 - (word & 1)
    fixed_slack = [[v, u, slack[u, v]] for v, u in product((0, 1), repeat=2)]
    return {"supports": stars, "all_full_old_words_extend": len(old),
            "old_projection_equals_actual_reached_source": True, "canonical_supports": by_scope,
            "exterior": exterior, "owner_lists": dict(owners), "live_and_loose": loose,
            "preparation": {"old_launches": len(old), "independent_fair_auxiliary_launches": len(old) << 27,
                            "invalid_auxiliary_launches": (len(old) << 27) - prices["lawful"],
                            "lawful_nonready_auxiliary_launches": prices["lawful"] - prices["ready"],
                            "lawful_joined_launches": prices["lawful"], "ready_auxiliary_launches": prices["ready"],
                            "ready_given_fixed_source_word_extensions": 1,
                            "counts_by_u0_then_required_slack": {str(key): n for key, n in slack.items()},
                            "legal_default_ready_with_fixed_slack_by_slack_then_u0": fixed_slack}}


def funding(stars, law, arm="ordinary"):
    prior = precedent()
    engine, reference, compact = prior.archives()
    expected, owners = prior.proposal(stars)
    delivered, proof = reference.grow(stars, law, arm, engine)
    assert expected["status"] == proof["status"]
    assert dict(expected["shortages"]) == proof.get("shortages", {})
    result = {"status": proof["status"], "planned": expected, "births": [], "rule": arm}
    if delivered is not None:
        assert len(proof["births"]) == len(expected["all_groups_if_funded"])
        assert tuple(b["parents"] for b in proof["births"]) == expected["all_groups_if_funded"]
        assert tuple(b["D"] for b in proof["births"]) == expected["lookahead_demands"]
        assert all(len(owners[d]) == 1 for b in proof["births"] for d in b["inputs"])
        expected_compact = compact.step(compact.from_stars(stars), law)
        assert expected_compact.status == "extend"
        assert expected_compact.fresh == tuple(b["q"] for b in proof["births"])
        with legal_solver(stars, law) as solver:
            for b in proof["births"]:
                received = tuple(sorted((owners[d][0], d) for d in b["inputs"]))
                projected = words_on(solver, tuple(d for _, d in received))
                implication = all(allowed(encode(tuple(d for _, d in received), w), mask(b["inputs"]), law)
                                  for w in projected)
                assert implication == b["old_inputs_already_imply_law"]
                result["births"].append(b | {"paid_pairs": received, "input_projection": projected})
        after, _ = prior.proposal(delivered)
        result |= {"stars_after": delivered, "following_actual_funding": after,
                   "focal_names_consumed": sorted(d for b in proof["births"] for d in b["inputs"] if d in FOCAL)}
    return result


def bare_controls(law):
    prior = precedent()
    owners, share, _ = prior.incidence(OLD)
    exchange = {k: [(a, b) for i, a in enumerate(row) for b in row[i + 1:] if owners[a] == owners[b]]
                for k, row in enumerate(OLD)}
    motifs = []
    for center, ends in owners.items():
        if len(ends) != 2:
            continue
        left, right = ends
        available = {k: tuple(d for d in OLD[k] if owners[d] == [k]) for k in ends}
        motifs.append({"center": center, "real_holders": ends, "outer_names_at_each_holder": available,
                       "concerted_offer_supported": all(available.values())})
    assert not exchange[0] and all(not m["concerted_offer_supported"] for m in motifs)
    first = funding((U,), law)
    assert tuple(first["stars_after"]) == OLD
    issued = [set(b["fresh"]) for b in first["births"]]
    assert all(not x.intersection(y) for i, x in enumerate(issued) for y in issued[i + 1:])
    return {"initial_reached_from_ordinary": first, "all_same_holder_bills_swaps": exchange,
            "attempted_concerted_cut": motifs, "root_has_no_private_names": True,
            "any_rereading_root_crossing_in_supported_class": False,
            "owner_lists": dict(owners), "natively_issued_same_cut_names_are_disjoint": True,
            "later_attempts": {arm: funding(OLD, law, arm) for arm in ARMS}}


@dataclass(frozen=True)
class Offer:
    name: str
    acting_holder: int
    pair: tuple
    guard: tuple = ()
    stage: str = ""


@dataclass(frozen=True)
class Case:
    key: str
    kind: str = "full"
    mode: str = "asymmetric"
    decode: str = "native"
    threshold: int = 0
    answer: str = "unanimity"
    off: tuple = ()


def offer(name, acting, pair, guard=(), stage=""):
    return Offer(name, acting, tuple(pair), tuple(guard), stage)


def guarded_rows(law):
    rows = {}
    for before in product((0, 1), repeat=3):
        if len(set(before)) == 1:
            decoded = before[0] if law == "parity" else 1 - before[0]
            rows[before + (0, 0)] = decoded
            continue
        s1 = (before[1], before[2], before[0])
        s0 = (before[2], before[0], before[1])
        signatures = [tuple(x ^ y for x, y in zip(before[:2], after[:2], strict=True)) for after in (s0, s1)]
        assert len(set(signatures)) == 2 and (0, 0) not in signatures
        for decoded, sign in enumerate(signatures):
            rows[before + sign] = decoded
    return rows


def extraction(case, law):
    if case.mode not in ("symmetric", "asymmetric", "restricted"):
        return ()
    groups = []
    decoded_law = law if case.decode == "native" else case.decode
    for i, row in enumerate(ROWS, 1):
        a, b, c = row
        t0, t1, q = TQ[i - 1]
        capture = [(offer(f"H.capture{i}.{j}", H, t, [(row[j], 1)], "capture"),)
                   for j, t in enumerate((t0,) if case.mode == "restricted" else (t0, t1))]
        f = i + 1
        forward = [(offer(f"F{i}.advance01", f, (a, b), [(i, 1)], f"F{i}"),)]
        if case.mode != "restricted":
            forward += [(offer(f"F{i}.advance12", f, (b, c), [(i, 1)], f"F{i}"),)]
        if case.mode == "symmetric":
            forward += [(offer(f"F{i}.advance12.zero", f, (b, c), [(i, 0)], f"F{i}"),),
                        (offer(f"F{i}.advance01.zero", f, (a, b), [(i, 0)], f"F{i}"),)]
        backward = [(offer(g[0].name.replace("advance", "return"), g[0].acting_holder,
                           g[0].pair, g[0].guard, g[0].stage),) for g in reversed(forward)]
        groups.extend(capture + forward + capture + backward)
        if case.mode == "restricted":
            continue
        patterns = guarded_rows(decoded_law) if case.mode == "symmetric" else {
            bits: int(any(bits[3:]) or bits[:3] == ((1, 1, 1) if decoded_law == "parity" else (0, 0, 0)))
            for bits in product((0, 1), repeat=5)
        }
        scope = (*row, t0[1], t1[1])
        groups.append(tuple(offer(f"H.compare{i}.{number}", H, q, zip(scope, pattern, strict=True), "capture")
                            for number, (pattern, inference) in enumerate(sorted(patterns.items())) if inference))
    return tuple(groups)


def writing(case, law):
    patterns = []
    if case.mode == "passive":
        scope = tuple(d for row in ROWS for d in row)
        patterns = [((bit,) * 9, bit) for bit in (0, 1)]
    elif case.mode in ("proxy", "local_value", "parity_slack"):
        scope = (TQ[0][2][1] if case.mode == "proxy" else ROWS[0][0] if case.mode == "local_value" else H_PRIVATE,)
        patterns = [((value,), 1 - value if case.mode == "parity_slack" else value) for value in (0, 1)]
    elif case.mode == "restricted":
        scope = tuple(d for row, bank in zip(ROWS, TQ, strict=True) for d in (*row[:2], bank[0][1]))
        for c in (0, 1):
            patterns.extend((sum(((*pair, c) for pair in pairs), ()), 1 - c)
                            for pairs in product(((0, 1), (1, 0)), repeat=3))
    elif case.mode == "asymmetric":
        scope = tuple(bank[2][1] for bank in TQ)
        if case.answer == "xor":
            patterns = [(bits, sum(bits) % 2) for bits in product((0, 1), repeat=3)]
        else:
            patterns = [((bit,) * 3, 1 - bit) for bit in (0, 1)]
    elif case.mode == "symmetric":
        rows = guarded_rows(law if case.decode == "native" else case.decode)
        scope = tuple(d for row, (t0, t1, q) in zip(ROWS, TQ, strict=True) for d in (*row, t0[1], t1[1], q[1]))
        valid = {c: sorted((*pattern, c) for pattern, decoded in rows.items() if decoded == c) for c in (0, 1)}
        tests = [(0, 0, 0), (1, 1, 1)] if case.answer != "xor" else list(product((0, 1), repeat=3))
        for test in tests:
            target = sum(test) % 2 if case.answer == "xor" else 1 - test[0]
            for entries in product(*(valid[c] for c in test)):
                moves = sum(any(pattern[3:5]) for pattern in entries)
                if moves >= case.threshold:
                    patterns.append((sum(entries, ()), target))
    words = tuple(offer(f"H.write.{number}", H, (B, C) if target == 0 else (A, C),
                        zip(scope, pattern, strict=True), "write")
                  for number, (pattern, target) in enumerate(patterns))
    return (words,) if words else ()


DELIVERY = ((offer("K.deliver.0", K, (E, F), zip(ABC, ZERO, strict=True), "delivery"),
             offer("K.deliver.1", K, (D, F), zip(ABC, ONE, strict=True), "delivery")),)


def single_offer(case):
    if case.mode == "single_F":
        return ((offer("F1.single01", 2, ROWS[0][:2], ((1, 1),), "F1"),),)
    bit = int(case.mode == "single_H_one")
    return ((offer(case.mode, H, (A, C) if bit else (B, C),
                   ((d, bit) for row in ROWS for d in row), "write"),),)


def roster(case, law):
    if case.mode.startswith("single_"):
        return {"extract": (), "write": single_offer(case), "deliver": (), "erase": (), "return": ()}
    groups = extraction(case, law)
    writer = writing(case, law)
    return {"extract": groups, "write": writer, "deliver": DELIVERY,
            "erase": tuple(reversed(writer)), "return": tuple(reversed(groups))}


def eligibility(stars, owners, move, off):
    holding = set(stars[move.acting_holder])
    a, b = move.pair
    assert a != b and len({d for d, _ in move.guard}) == len(move.guard)
    assert not set(move.pair).intersection(d for d, _ in move.guard)
    assert all(v in (0, 1) for _, v in move.guard)
    if move.stage in off or "all" in off:
        return "disconnected"
    if a not in holding or b not in holding or owners[a] != owners[b] or any(d not in holding for d, _ in move.guard):
        return "unsupported"
    return "offered"


def compile_groups(groups, stars, off):
    owners = precedent().incidence(stars)[0]
    compiled = []
    for group in groups:
        visit = Counter()
        scope = tuple(sorted(d for d, _ in group[0].guard))
        spec = {}
        for move in group:
            assert tuple(sorted(d for d, _ in move.guard)) == scope
            grade = eligibility(stars, owners, move, off)
            visit[grade] += 1
            match = sum(v << d for d, v in move.guard)
            if grade == "offered":
                assert match not in spec
                spec[match] = (mask(move.pair), move)
        compiled.append((mask(scope), spec, visit))
    return tuple(compiled)


def run_offer_group(word, group):
    scope, spec, counts = group
    row = spec.get(word & scope)
    if row is None:
        return word, None, None
    pair, move = row
    moved = (word & pair) not in (0, pair)
    return word ^ pair if moved else word, move, moved


def summaries(word):
    return {"word": word, "H_shared_ABC": values(word, ABC), "K_word": values(word, ABC + DEF + (K_PRIVATE,)),
            "L_word": values(word, DEF + (L_PRIVATE,)), "Q": [values(word, bank[2]) for bank in TQ],
            "T": [[values(word, pair) for pair in bank[:2]] for bank in TQ]}


def run_schedule(initial, schedules, traced=False):
    word = initial
    actual = [0, 0, 0]
    checkpoints = {}
    statuses = Counter()
    trace = {}
    for stage, onsets in schedules.items():
        for index, block in enumerate(onsets):
            old = word
            word, move, fired = run_offer_group(word, block)
            if traced:
                counts = Counter(block[2])
                counts["refused_guard"] = counts.pop("offered", 0) - int(move is not None)
                if move is not None:
                    counts["fired" if fired else "equal_operands"] += 1
                statuses.update(counts)
                trace.setdefault(stage, []).append({
                    "group_index": index, "visited_by_disposition": dict(counts), "matched_if_any": move.name if move else None,
                    "old_word": old, "new_word": word,
                })
            if fired and move is not None and (
                    stage == "extract" and ".advance" in move.name or stage == "write" and ".single" in move.name):
                actual[int(move.name[1]) - 1] += 1
        if traced or stage in ("extract", "write", "deliver"):
            checkpoints[stage] = word
    return {"end": word, "before_restore": checkpoints.get("deliver", checkpoints.get("write", word)),
            "after_extract": checkpoints.get("extract", initial), "motion": tuple(actual),
            "trace": trace, "statuses": dict(statuses), "checkpoints": checkpoints}


def compact_schedule(schedule):
    return {stage: [[{"id": m.name, "acting_holder": m.acting_holder,
                      "swap": m.pair, "guard_literals": m.guard, "departure_stage": m.stage} for m in group]
                    for group in blocks] for stage, blocks in schedule.items()}


def cases(law):
    subjects = [Case("asymmetric"), Case("symmetric", mode="symmetric"),
                Case("symmetric_one", mode="symmetric", threshold=1),
                Case("symmetric_all", mode="symmetric", threshold=3),
                Case("restricted", kind="restricted", mode="restricted"),
                Case("passive", mode="passive"),
                Case("supplied_copy", mode="proxy"), Case("local_read_of_x10", mode="local_value"),
                *(Case(key, mode=key) for key in ("single_F", "single_H_zero", "single_H_one"))]
    if law == "parity":
        subjects.extend((
            Case("asymmetric_xor", answer="xor"),
            Case("symmetric_xor", mode="symmetric", answer="xor"),
            Case("asymmetric_nae_decoder", decode="nae"),
            Case("symmetric_nae_decoder", mode="symmetric", decode="nae"),
            Case("supplied_slack", mode="parity_slack"),
        ))
    active = [case for case in subjects if case.mode in ("symmetric", "asymmetric", "restricted")]
    for case in active:
        for disconnected in (("F1",), ("F2",), ("F3",), ("F1", "F2", "F3")):
            key = case.key + "__off_" + "_".join(disconnected)
            subjects.append(Case(key, case.kind, case.mode, case.decode, case.threshold, case.answer, disconnected))
    for mode in ("asymmetric", "symmetric"):
        for disabled in ("capture", "write", "delivery", "all"):
            subjects.append(Case(f"{mode}__off_{disabled}", mode=mode, off=(disabled,)))
        for missing in tuple(d for row in ROWS for d in row):
            subjects.append(Case(f"{mode}__omit_{missing}", kind=f"omit_{missing}", mode=mode))
    return tuple(subjects)


def named_roles():
    return {"holders": {"R": 0, "F0": 1, "F1": 2, "F2": 3, "F3": 4, "H": H, "K": K, "L": L},
            "u": U, "focal": FOCAL, "x": ROWS, "ABC": ABC, "DEF": DEF, "hks": (H_PRIVATE, K_PRIVATE, L_PRIVATE),
            "T_and_Q": {f"F{i}": {"T0": a, "T1": b, "Q": c}
                        for i, (a, b, c) in enumerate(TQ, 1)}}


@cache
def input_profiles(law):
    """One physical replay per nonfocal basis word, with exact focal multiplicity."""
    grouped = defaultdict(list)
    for word in old_words(law):
        grouped[word & ~FOCAL_SCOPE].append(word)
    assert all(len(panel) == (4 if law == "parity" else 7) for panel in grouped.values())
    return tuple((profile, panel[0], len(panel)) for profile, panel in sorted(grouped.items()))


def port(word):
    return {READY: "ready", ZERO: "0", ONE: "1"}[values(word, DEF)]


def trace_examples(samples, schedules, supports, law):
    found = []
    reversed_moves = {"inverse": tuple(block for steps in reversed(tuple(schedules.values())) for block in reversed(steps))}
    for word in sorted(samples):
        result = run_schedule(word, schedules, traced=True)
        final = result["end"]
        assert all(allowed(v, row, law) for v in result["checkpoints"].values() for row in supports)
        reset = run_schedule(final, reversed_moves)["end"]
        assert reset == word and run_schedule(reset, schedules)["end"] == final
        idle = run_schedule(final, {"idle": schedules["deliver"]})["end"]
        assert idle == final
        repeated = run_schedule(final, schedules)["end"]
        if port(final) != "ready":
            assert port(repeated) == "ready"
        tested_focal_fibres = 0
        for focal in product((0, 1), repeat=len(FOCAL)):
            changed = (word & ~FOCAL_SCOPE) | encode(FOCAL, focal)
            if not allowed(changed, mask(OLD[1]), law):
                continue
            lifted = run_schedule(changed, schedules, traced=True)
            assert {key: v & ~FOCAL_SCOPE for key, v in result["checkpoints"].items()} == {
                key: v & ~FOCAL_SCOPE for key, v in lifted["checkpoints"].items()}
            assert lifted["statuses"] == result["statuses"]
            for stage, traced in result["trace"].items():
                carried = lifted["trace"][stage]
                assert [(x["visited_by_disposition"], x["matched_if_any"]) for x in carried] == [
                    (x["visited_by_disposition"], x["matched_if_any"]) for x in traced]
            assert lifted["end"] & FOCAL_SCOPE == changed & FOCAL_SCOPE
            tested_focal_fibres += 1
        assert tested_focal_fibres == (4 if law == "parity" else 7)
        found.append({"initial": summaries(word), "after_extraction": summaries(result["after_extract"]),
                      "before_restoring": summaries(result["before_restore"]), "final": summaries(final),
                      "status_counts": result["statuses"], "actual_motion_at_each_sibling": result["motion"],
                      "reread": port(final), "idle_offers_leave_same_word": idle == final,
                      "full_inverse_restores_initial": True, "second_delivery_after_clear_repeats_word": True,
                      "identical_untouched_focal_variant_transcripts": tested_focal_fibres,
                      "blind_repeat": summaries(repeated), "offers_by_stage": result["trace"]})
    return found


def replay_case(case, law):
    board = apparatus(case.kind)
    layout = roster(case, law)
    for groups in layout.values():
        for block in groups:
            for m in block:
                assert not set(m.pair).intersection(range(7))
                assert all(d not in (0, *FOCAL) for d, _ in m.guard)
                assert case.mode == "parity_slack" or all(d != H_PRIVATE for d, _ in m.guard)
    schedules = {stage: compile_groups(groups, board, case.off) for stage, groups in layout.items()}
    allowed_supports = tuple(map(mask, board))
    hist = Counter()
    true_calls = Counter()
    intermediate = Counter()
    issued_messages = Counter()
    examples = {}
    outcomes = {}
    settings_set = not case.mode.startswith("single_")

    for profile, word, count in input_profiles(law):
        before = ready(word, board, law, case.mode == "proxy")
        result = run_schedule(before, schedules)
        final = result["end"]
        assert ((final ^ word) & FOCAL_SCOPE) == 0
        assert all(allowed(final, support, law) for support in allowed_supports)
        if settings_set:
            assert (final ^ before) & ~mask(DEF) == 0
        resulting = port(final)
        expects = str(word & 1)
        abc = "".join(str(v) for v in values(result["before_restore"], ABC))
        intermediate[expects, abc, resulting] += count
        if case.mode in ("symmetric", "asymmetric"):
            expected = values(word, U[1:])
            actual = tuple(values(result["after_extract"], bank[2])[1] for bank in TQ)
            if case.decode == "native" and not case.off and case.kind == "full":
                assert actual == expected
            issued_messages[expected, actual] += count
        moved = sum(n > 0 for n in result["motion"])
        exact_swaps = sum(result["motion"])
        call = "ready" if resulting == "ready" else "correct" if resulting == expects else "wrong"
        hist[expects, resulting, moved, exact_swaps] += count
        true_calls[call] += count
        outcomes[profile] = (expects, resulting, moved, exact_swaps)
        examples.setdefault((expects, abc, resulting, moved), before)

    assert sum(true_calls.values()) == len(old_words(law))
    moves_table = [[*translation, mass] for translation, mass in sorted(hist.items())]
    record = {
        "apparatus": case.kind, "mode": case.mode, "disabled": case.off,
        "visibility": {"ready_plan": "supplied_u0_copy" if case.mode == "proxy" else "prepared_default",
                       "forms_and_wires_are_additions": True, "uses_actual_H_slack": case.mode == "parity_slack"},
        "launches": len(old_words(law)), "distinct_replayed_nonfocal_words": len(outcomes),
        "by_true_u0_result_number_of_moving_siblings_and_elementary_moves": moves_table,
        "orientation_H_write_before_restore_and_final_L_port": [[*key, n] for key, n in sorted(intermediate.items())],
        "literal_Q_messages_against_true_u123": [[*key, n] for key, n in sorted(issued_messages.items())],
        "totals": dict(true_calls),
        "fault_sizes": {stage: [dict(block[2]) for block in blocks] for stage, blocks in schedules.items()},
        "example_trajectories": trace_examples(examples.values(), schedules, allowed_supports, law),
    }
    if case.key in ("asymmetric", "symmetric", "symmetric_one", "symmetric_all", "restricted",
                    "passive", "symmetric_xor", "single_F", "single_H_zero", "single_H_one"):
        record["ordered_offer_groups"] = compact_schedule(layout)
    return record, outcomes


def matched_controls(cases_by_key, staged, law):
    result = {}
    mult = {profile: count for profile, _, count in input_profiles(law)}
    for key in sorted(cases_by_key):
        fixed = key + "__off_F1_F2_F3"
        if fixed not in cases_by_key:
            continue
        base, nil = staged[key], staged[fixed]
        comparisons = Counter()
        for profile, main in base.items():
            contrary = nil[profile]
            assert contrary[0] == main[0] and contrary[2:] == (0, 0)
            comparisons[(main[0], main[1], contrary[1])] += mult[profile]
        result[key] = [[*row, n] for row, n in sorted(comparisons.items())]
    return result


def transported_name(word, renaming):
    return sum(1 << new for old, new in renaming.items() if word & (1 << old))


def transports(records, law):
    """Verify all four physically transported focal roles and a reversed keeper marking."""
    original = records["symmetric_xor" if law == "parity" else "symmetric_all"]
    samples = original["example_trajectories"]
    selected = [next(row for row in samples if row["reread"] == label) for label in ("0", "1")]
    board = apparatus("full")
    schedule = roster(Case("focal_transport", mode="symmetric", threshold=0 if law == "parity" else 3,
                           answer="xor" if law == "parity" else "unanimity"), law)
    report = []
    for i in range(4):
        rng = Random(20261122030 + i)
        permuted = list(range(len(board)))
        rng.shuffle(permuted)
        old_to_holder = {v: k for k, v in enumerate(permuted)}
        names = tuple(range(43))
        encoded = list(names)
        for j in range(4):
            encoded[U[j]] = U[(j + i) % 4]
            all_data = (FOCAL, *ROWS)
            for n, m in zip(all_data[j], all_data[(j + i) % 4], strict=True):
                encoded[n] = m
        if i % 2:
            encoded[A], encoded[B] = B, A
            encoded[D], encoded[E] = E, D
            for p, q in (pair for bank in TQ for pair in bank):
                encoded[p], encoded[q] = q, p
        mapping = dict(zip(names, encoded, strict=True))
        transported_board = tuple(tuple(mapping[d] for d in board[k]) for k in permuted)
        translated = {}
        for stage, groups in schedule.items():
            carried = tuple(tuple(offer(m.name, old_to_holder[m.acting_holder], (mapping[d] for d in m.pair),
                                        ((mapping[d], v) for d, v in m.guard), m.stage)
                                  for m in group) for group in groups)
            translated[stage] = compile_groups(carried, transported_board, ())
        for sample in selected:
            start = transported_name(sample["initial"]["word"], mapping)
            final = transported_name(sample["final"]["word"], mapping)
            assert run_schedule(start, translated)["end"] == final
            assert values(final, tuple(mapping[d] for d in DEF)) == values(sample["final"]["word"], DEF)
        report.append({"image_of_F0_original_paid": encoded[U[0]], "image_of_focal_names": [encoded[d] for d in FOCAL],
                       "name_transport": mapping, "encoded_holder_to_original": permuted,
                       "new_physical_stars": transported_board, "replayed_both_written_answers": True,
                       "physically_reversed_bank_marking": bool(i % 2)})
    return report


def source_hashes():
    approved_path = HERE / "advisor_receipt.json"
    entry = next(r for r in json.loads(approved_path.read_bytes())["records"] if r["verdict"] == "approved")
    contract = HERE / "preregistration.md"
    assert sha256(contract.read_bytes()).hexdigest() == entry["sha256"]
    assert sha256((ROOT / entry["candidate_path"]).read_bytes()).hexdigest() == entry["sha256"]
    prior = precedent()
    first, second, third = prior.archives()
    dependencies = [Path(__file__), approved_path, contract, ROOT / entry["candidate_path"],
                    PAST / "native.py", PAST / "native.json.gz", ROUTES,
                    *(Path(module.__file__) for module in (first, second, third, first.S, first.J, first.F))]
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in dependencies}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "native.json.gz")
    args = parser.parse_args()
    hashes = source_hashes()
    out = {}
    for law in LAWS:
        entries = cases(law)
        alternatives = sorted({c.kind for c in entries})
        boards = {kind: projected_apparatus(kind, law) | {"ordinary_next": funding(apparatus(kind), law)}
                  for kind in alternatives}
        controls = {}
        histories = {}
        for row in entries:
            controls[row.key], histories[row.key] = replay_case(row, law)
        out[law] = {"bare": bare_controls(law), "old_complete_words_lsb_name_zero": old_words(law),
                    "apparatus": boards, "controls": controls,
                    "paired_all_F_disabled_on_same_word": matched_controls(controls, histories, law),
                    "recoded_focal_and_keeper_roles": transports(controls, law),
                    "reverse_scorer_only": {"original_ordinary_word_unchanged": True,
                                          "ports_over_interpretation_only": {"0": "1", "1": "0", "ready": "ready"}}}
    receipt = {"schema": "b302-native-v1", "roles": named_roles(), "laws": out, "source_hashes_sha256": hashes}
    blob = (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode()
    scratch = args.output.with_suffix(".tmp")
    scratch.write_bytes(gzip.compress(blob, mtime=0))
    scratch.replace(args.output)
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()

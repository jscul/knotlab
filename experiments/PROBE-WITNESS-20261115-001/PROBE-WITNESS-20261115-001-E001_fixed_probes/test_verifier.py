"""Synthetic independent geometry, raw-row, fallback and mutation checks."""

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import random

from verifier import PaidVerifier, _JointChecker


def _synthetic_solver(n):
    path = Path(__file__).resolve().parents[3] / (
        "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/joint_solver.py")
    spec = spec_from_file_location("_probe_synthetic_solver", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.JointSolver(n)


def group_mask(group):
    return sum(1 << i for i in group)


def raw_rows(n, group, local, scheme, setting):
    result = []
    for s in local:
        row = 0
        for i in range(n):
            if i in group:
                bit = (s >> group.index(i)) & 1
            else:
                bit = 0 if scheme == 0 else int((i // scheme) % 2 == 0)
                bit ^= setting
            row |= bit << i
        result.append(row)
    return result


def actual_cert(n, tables, group, scheme, settings):
    by = {}
    for s in range(8):
        joint = []
        for setting in (0, 1):
            if settings & (1 << setting):
                row, = raw_rows(n, group, (s,), scheme, setting)
                joint.extend((t >> row) & 1 for t in tables)
        by.setdefault(tuple(joint), s)
    if len(by) >= 3:
        a, b, c = list(by.values())[:3]
        return [group_mask(group), a, b, c, settings, scheme]
    return None


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("invalid witness, cut or physical program accepted")


def check():
    n = 6
    solver, verifier, original = _synthetic_solver(n), PaidVerifier(n), _JointChecker(n)
    groups = tuple(combinations(range(n), 3))
    parity = sum((r.bit_count() % 2) << r for r in range(1 << n))
    any_true = sum(int(r != 0) << r for r in range(1 << n))
    tables = (parity, any_true)
    result = solver.solve(tables)
    assert result["width"] == 2
    certs = [[group_mask(group), 0, 1, 3, 1, 0] for group in groups]
    for g, c in zip(groups, certs):
        assert c == actual_cert(n, tables, g, 0, 1)
    result["witnesses"] = certs
    assisted = verifier.verify(tables, result)
    unassisted = verifier.verify(tables, result, [])
    inherited = original.verify(tables, result)
    assert all(assisted[k] == unassisted[k] == v for k, v in inherited.items())
    assert assisted["accepted_witnesses"] == assisted["included_witnesses"] == len(groups)
    assert assisted["effective_witnesses"] == len(groups) - 1
    assert assisted["exact_alternatives"] == 0 and assisted["chosen_exact_classifications"] == 1
    assert unassisted["exact_alternatives"] == len(groups) - 1 and unassisted["verifier_row_reads"] == 0
    expected_rows = set()
    for group, cert in zip(groups, certs):
        expected_rows.update(raw_rows(n, group, cert[1:4], cert[5], 0))
    assert assisted["verifier_row_reads"] == len(expected_rows)
    assert assisted["verifier_row_requests"] == 3 * len(groups)
    assert assisted["verifier_row_requests"] - len(expected_rows) == assisted["verifier_row_cache_hits"]
    partial = verifier.verify(tables, result, certs[-1:])
    assert partial["exact_alternatives"] == len(groups) - 2 and partial["effective_witnesses"] == 1
    assert verifier.verify(tables, result)["verifier_row_reads"] == len(expected_rows)

    for bad in ([*certs[0][:4], 2, 0], [*certs[0][:4], 0, 0], [*certs[0][:5], 4], [7, False, 1, 3, 1, 0],
                [7, 1, 1, 3, 1, 0], [7, 0, 1, 8, 1, 0], [3, 0, 1, 3, 1, 0], [67, 0, 1, 3, 1, 0],
                [7, 0, 1, 3, 1], [7, 0, 1, 3, 1, 0, 99]):
        rejects(lambda: verifier.verify(tables, result, [bad]))
    rejects(lambda: verifier.verify(tables, result, [certs[0], certs[0]]))
    flipped = deepcopy(result)
    flipped["circuit"]["outputs"][0] = n
    rejects(lambda: verifier.verify(tables, flipped))
    bypass = deepcopy(result)
    bypass["summary_wires"] = [n, n + 1]
    rejects(lambda: verifier.verify(tables, bypass))
    forward = deepcopy(result)
    forward["circuit"]["gates"][0][0] = 999
    rejects(lambda: verifier.verify(tables, forward))
    changed = dict(result, class_count=result["class_count"] + 1)
    rejects(lambda: verifier.verify(tables, changed))

    # An otherwise valid witnessed triple can be irrelevant after a true
    # one-bit target is found. An invalid record still fails at width one.
    same = (parity, parity)
    small = solver.solve(same)
    assert small["width"] == 1
    rejects(lambda: verifier.verify(same, small, certs[-1:]))

    rng = random.Random(712499)
    random_pair = tuple(rng.getrandbits(1 << n) for _ in range(2))
    wide = solver.solve(random_pair)
    assert wide["width"] == 3
    covered = set()
    for scheme in range(4):
        for settings in (1, 2, 3):
            pack = [c for g in groups if (c := actual_cert(n, random_pair, g, scheme, settings))]
            assert pack
            receipt = verifier.verify(random_pair, wide, pack)
            assert receipt["accepted_witnesses"] == len(pack) and receipt["effective_witnesses"] == 0
            assert receipt["exact_alternatives"] == len(groups) - 1
            for g in groups:
                if actual_cert(n, random_pair, g, scheme, settings):
                    covered.add((g, scheme, settings))
    assert len(covered) >= 100

    # Both outputs equal a single scalar with independent residual functions
    # in the two outside settings. No single setting witnesses three values.
    axes = (0, 2, 5)
    g = sum((((r >> 0) ^ (r >> 2) ^ (r >> 5)) & 1 if r & 2
             else int(sum((r >> i) & 1 for i in axes) >= 2)) << r for r in range(1 << n))
    pair = (g, g)
    assert actual_cert(n, pair, axes, 0, 1) is None and actual_cert(n, pair, axes, 0, 2) is None
    double = actual_cert(n, pair, axes, 0, 3)
    assert double
    receipt = verifier.verify(pair, solver.solve(pair), [double])
    assert receipt["verifier_row_reads"] == 6 and receipt["accepted_witnesses"] == 1

    # The other group really needs two bits. Its valid >one-bit witness
    # cannot certify the falsely alleged minimum of three on a wider group.
    bits = (0, 2, 5)
    others = tuple(i for i in range(n) if i not in bits)
    data = [0, 0]
    outside_codes = ((0b10101110, 0b01100101), (0b00011001, 0b11100110))
    for r in range(1 << n):
        sub = sum(((r >> i) & 1) << j for j, i in enumerate(bits))
        z = sum(((r >> i) & 1) << j for j, i in enumerate(others))
        codes = (sub.bit_count() % 2, int(sub != 0))
        for o in range(2):
            data[o] |= ((outside_codes[o][codes[o]] >> z) & 1) << r
    valid = solver.solve(data)
    assert valid["width"] == 2
    wider = next(group for group in groups if original._classes(data, group) > 4)
    forged = dict(valid, triple=list(wider), summary_wires=list(wider), class_count=original._classes(data, wider), width=3)
    proofs = [c for group in groups if (c := actual_cert(n, data, group, 0, 3))]
    assert any(c[0] == group_mask(bits) for c in proofs)
    rejects(lambda: verifier.verify(data, forged, proofs))
    return len(covered)


if __name__ == "__main__":
    print(f"Passed synthetic verification, corruptions and {check()} raw group/scheme/settings checks.")

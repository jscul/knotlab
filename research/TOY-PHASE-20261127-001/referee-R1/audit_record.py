"""Verify the archived closure, certificate actions, and the boundary of the frozen record."""

import hashlib
import io
import itertools
import json
import subprocess
import sys
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
CENSUS = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
FREEZE = "675f3dc0ae"
CLOSE = "eff6bce09b"


def signature(word, holder_sets):
    return tuple(sum(word >> d & 1 for d in holder) % 2 for holder in holder_sets)


def check_fixture():
    # This is the only use of the growth engine. Derive the four signs and readers separately.
    sys.path.insert(0, str(ROOT / "research/FORBID-EDITS-20261126-001"))
    import forbid
    parents = ((0, 1, 2), (1, 3, 4), (3, 0, 5))
    expected = [sorted(group) for group in parents] + [[2, 4, 5]]
    grown, details = forbid.grow(parents, "parity", "ordinary", forbid.ENGINE)
    assert [sorted(group) for group in grown] == expected
    birth, = details["births"]
    assert birth["old_inputs_already_imply_law"] and birth["f"] == 0
    holders = list(map(set, expected))
    readers = [pair for pair in itertools.combinations(range(6), 2)
               if all(not set(pair) <= h for h in holders)]
    assert all(len(a & b) == 1 for a, b in itertools.combinations(holders, 2))
    assert all(sum(d in h for h in holders) == 2 for d in range(6))
    assert readers == [(0, 4), (1, 5), (2, 3)]
    signs = Counter(signature(w, holders) for w in range(64))
    assert len(signs) == 8 and all(sum(s) % 2 == 0 and n == 8 for s, n in signs.items())
    return {"knots": expected, "unheld pairs": readers, "births": 1, "fresh distinctions": 0,
            "next round": details["following_funding"]["status"],
            "counts by four sign bits in parent order then close":
                {"".join(map(str, k)): signs[k] for k in itertools.product(range(2), repeat=4)}}


def canonical_knots():
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.cli import main
    results = {}
    cases = [("even", "ABc", [1, 2, 4, 7]), ("odd", "ABc", [0, 3, 5, 6]),
             ("not-all-equal", "ABc", [0, 7]),
             ("four-place even", "ABch", [w for w in range(16) if w.bit_count() % 2])]
    for name, labels, forbidden in cases:
        width = len(labels)
        clauses = [" ".join(("~" if int(bit) else "") + d for bit, d in zip(f"{w:0{width}b}", labels))
                   for w in forbidden]
        output = io.StringIO()
        with redirect_stdout(output):
            assert main(["check", "--cnf", "; ".join(clauses), "--loops", *labels[:-1],
                         "--contact", labels[-1], "--json"]) == 0
        check = json.loads(output.getvalue())
        assert check["is_knot"] and len(check["allowed"]) == 2 ** width - len(forbidden)
        results[name] = {k: check[k] for k in ("allowed", "binding", "invisible_in_parts", "coexistence")}
    return results


def scope_examples():
    # The previously published four-place signed read relabels two outcomes.
    # Written on bits, it is an ordinary permutation of eight allowed words.
    def permute(word):
        a, b, c, h = word
        return a, 1 ^ c, b, 1 ^ h

    support = [w for w in itertools.product(range(2), repeat=4) if sum(w) % 2 == 0]
    assert set(map(permute, support)) == set(support)
    for word in support:
        a, b, c, h = word
        twice = permute(permute(word))
        assert twice == (a, b ^ 1, c ^ 1, h) and permute(permute(twice)) == word
    # Alternative stabilizer encoding: one qubit for each of the six distinctions.
    # A uniform vector on a binary linear code is stabilized by its X shifts
    # and its known Z parities. Check independence and their action explicitly.
    rows = [{0, 1, 2}, {1, 3, 4}, {0, 3, 5}, {2, 4, 5}]
    code = {w for w in range(64) if signature(w, rows) == (0, 0, 0, 0)}
    z_checks = [sum(1 << d for d in h) for h in rows[:3]]
    x_checks = []
    span = {0}
    for w in sorted(code - {0}):
        if w not in span:
            x_checks.append(w)
            span |= {s ^ w for s in span}
    assert span == code and len(x_checks) == 3
    z_span = {0}
    for mask in z_checks:
        assert all((w & mask).bit_count() % 2 == 0 for w in code)
        z_span |= {s ^ mask for s in z_span}
    assert len(z_span) == 8
    assert all({w ^ dx for w in code} == code for dx in x_checks)
    # Earlier closed-part reading: count only rules entirely present in each context.
    readers = [(3, 2), (0, 4), (1, 5)]
    correct_entries = even_entries = 0
    for settings in itertools.product(range(2), repeat=3):
        bits = [r[s] for r, s in zip(readers, settings)]
        read = set(bits)
        z_counts = Counter(tuple(w >> d & 1 for d in bits) for w in code)
        ans = list(itertools.product(range(2), repeat=3))
        part = [w for w in ans if all(sum(w) % 2 == (index == 3)
                                      for index, rule in enumerate(rows) if rule <= read)]
        for w in ans:
            even_eighths = 2 * (sum(w) % 2 == 0) if sum(settings) % 2 else 1
            even_entries += z_counts[w] == even_eighths
            want_eighths = (2 * (sum(w) % 2 == (sum(settings) == 3))
                            if sum(settings) % 2 else 1)
            correct_entries += 8 * (w in part) == want_eighths * len(part)
    assert correct_entries == even_entries == 64
    return {"four-place value permutation in (a,b,c,h) order":
                {"".join(map(str, w)): "".join(map(str, permute(w))) for w in support},
            "order": 4, "square flips": ["b", "c"], "fixed read": "a",
            "counting separately in each context, odd target entries matched": correct_entries,
            "six-qubit uniform pure stabilizer state": {"X shifts": x_checks, "Z checks": z_checks,
                                                        "even table entries matched": even_entries}}


def action(ops, indices, word=0):
    """Apply a listed product rightmost first to a binary basis word."""
    exponent = 0
    for d in reversed(indices):
        phase, change, question = ops[d]
        exponent += phase + 2 * (question & word).bit_count()
        word ^= change
    return word, exponent % 4


def restored(sharing, n):
    neighbors = [set() for _ in range(n)]
    for u, v in sharing:
        neighbors[u].add(v)
        neighbors[v].add(u)
    # Each punctured roster must remain connected in the reachability criterion.
    for omitted in range(n):
        remain = set(range(n)) - {omitted}
        reached = {min(remain)}
        while True:
            nxt = (reached | set.union(*(neighbors[u] for u in reached))) & remain
            if nxt == reached:
                break
            reached = nxt
        if reached != remain:
            return []
    possible = []
    for last, parents in enumerate(neighbors):
        other = [group for v, group in enumerate(neighbors) if v != last]
        if any(parents <= group for group in other):
            continue
        if all(any(a in group and b in group for group in other)
               for a, b in itertools.combinations(parents, 2)):
            possible.append(last)
    return possible


def verify_certificate(row, index):
    ops, sharing = row["pauli_i_phase_X_bits_Z_bits"], row["sharing"]
    n = row["n"]
    holders = [[d for d, pair in enumerate(sharing) if h in pair] for h in range(n)]
    assert all(len(set(pair)) == len(pair) == 2 for pair in sharing)
    assert all(len(h) >= 3 for h in holders)
    assert len(ops) == len(sharing)
    nbits = max(max(x, z).bit_length() for _, x, z in ops)
    probes = [0] + [1 << j for j in range(nbits)]
    # Every word changes by the same XOR. Its sign is a constant times a binary
    # character, determined by the value at zero and at the single-bit words.
    assert all(action(ops, [d, d], w) == (w, 0) for d in range(len(ops)) for w in probes)
    assert all(x or z for _, x, z in ops)
    signs = []
    for h in holders:
        for a, b in itertools.combinations(h, 2):
            assert action(ops, [a, b]) == action(ops, [b, a])
            _, x, z = ops[a]
            _, u, v = ops[b]
            assert ((x & v).bit_count() + (z & u).bit_count()) % 2 == 0
        result_word, exponent = action(ops, h)
        assert result_word == 0 and exponent in (0, 2)
        assert all(action(ops, h, w) == (w, exponent) for w in probes)
        signs.append((-1) ** (exponent // 2))
        # These probe answers determine the unsigned toy parity at every underlying word.
        assert all(sum((ops[d][coord] & w).bit_count() for d in h) % 2 == 0
                   for coord in (1, 2) for w in probes)
    odd = [j for j, s in enumerate(signs) if s == -1]
    assert len(odd) % 2 == 1
    listing = sum(holders, [])
    assert all(action(ops, listing, w) == (w, 2) for w in probes)
    # Cancel equal occurrences by moving the second through intervening reads.
    remaining = listing[:]
    minus_swaps = 0
    while remaining:
        a = remaining.pop(0)
        j = remaining.index(a)
        minus_swaps += sum(action(ops, [a, b]) != action(ops, [b, a]) for b in remaining[:j])
        remaining.pop(j)
    assert minus_swaps % 2 == 1
    # Reversing the same toy answer at both appearances is an admissible relabel.
    flipped = [int(0 in h) for h in holders]
    assert sum(flipped) == 2
    return {"census index": index, "holders": n, "distinctions": len(ops), "nontrivial bits": nbits,
            "negative holders": odd, "negative adjacent exchanges during cancellation": minus_swaps,
            "odd toy holders after reversing distinction zero": [i for i in range(n) if flipped[i]],
            "possible last holders": restored(sharing, n)}


def check_census():
    entries = json.loads(CENSUS.read_text())
    rows = []
    by_size = {}
    for i, raw in enumerate(entries):
        size = str(raw["n"])
        counts = by_size.setdefault(size, dict(types=0, reached=0, certificates=0, reached_certificates=0))
        counts["types"] += 1
        last = restored(raw["sharing"], raw["n"])
        assert last == raw["restored_last_holders"]
        counts["reached"] += bool(last)
        if raw["pauli_i_phase_X_bits_Z_bits"] is None:
            assert not raw["operator"]
            continue
        assert raw["operator"]
        result = verify_certificate(raw, i)
        counts["certificates"] += 1
        counts["reached_certificates"] += bool(last)
        rows.append(result)
    # Compare only after reconstructing the actions from the external archive.
    recorded = json.loads((STUDY / "stress_certificates.json").read_text())["rows"]
    assert len(rows) == len(recorded)
    for r, h in zip(rows, recorded, strict=True):
        assert (r["census index"], r["holders"], r["distinctions"], bool(r["possible last holders"])) == (
            h["type"], h["holders"], h["distinctions"], h["grown"])
        assert all(h[k] is True for k in ("certificate holders commute",
                                         "toy questions commute within holders", "toy laws even in every holder"))
        assert h["reordering cost"] == h["certificate charge"] == -1
    return {"census sha256": hashlib.sha256(CENSUS.read_bytes()).hexdigest(),
            "population": len(entries), "certificates": len(rows), "by holder count": by_size,
            "total certified holders": sum(r["holders"] for r in rows),
            "stored odd holder counts": dict(Counter(len(r["negative holders"]) for r in rows)),
            "rows": rows}


def provenance():
    prefix = str(STUDY.relative_to(ROOT))

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)

    readme = prefix + "/README.md"
    main = prefix + "/toy_phase.py"
    before = git("show", FREEZE + ":" + readme)
    after = git("show", CLOSE + ":" + readme)
    assert after.startswith(before) and after[len(before):].lstrip().startswith(b"## Stress test")
    assert git("show", FREEZE + ":" + main) == git("show", CLOSE + ":" + main)
    artifacts = ["README.md", "toy_phase.py", "results.json", "stress_certificates.py",
                 "stress_certificates.json"]
    for name in artifacts:
        assert git("show", CLOSE + ":" + prefix + "/" + name) == git(
            "show", "a6927906c3:" + prefix + "/" + name)
    decision = prefix + "/decision.md"
    assert git("show", "a6927906c3:" + decision).startswith(git("show", CLOSE + ":" + decision))
    return {"freeze": FREEZE, "closure": CLOSE, "original code unchanged": True,
            "as-sent report appended at": "a6927906c3",
            "frozen README unchanged as prefix": True, "closed files verified": artifacts,
            "files at freeze": git("ls-tree", "-r", "--name-only", FREEZE, prefix).decode().splitlines()}


if __name__ == "__main__":
    summary = {"history": provenance(), "one round of growth": check_fixture(),
               "canonical checks": canonical_knots(), "scope examples": scope_examples(),
               "certificates": check_census()}
    (HERE / "audit_record.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(summary["one round of growth"])
    print(summary["certificates"]["by holder count"], summary["certificates"]["total certified holders"])

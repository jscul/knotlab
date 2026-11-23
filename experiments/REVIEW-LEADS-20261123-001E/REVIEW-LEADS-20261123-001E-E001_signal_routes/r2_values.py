"""R2, values.  For 64 lawful valued versions of each start per law (seed 2026112305) the births, their
parents and their numbers of fresh distinctions are identical.  Injected fault: the join veto of the
written-bit study; the check must flag a difference.

A valued version of a start is an allowed word of the start under the law, drawn uniformly (parity by
exact linear algebra over GF(2); not-all-equal by rejection from uniform words).  Valued growth hands
each fresh distinction a value drawn uniformly from the lawful completions given its paid inputs
(a birth with no fresh distinctions must already be lawful).  The births of each valued run are read
back from its recorded frames and compared with the births of the unvalued reference run.

The join veto (research/WRITTEN-BIT-AND-JOIN-VETO-20261122-001/design_candidate.md, experiments/
WRITTEN-BIT-AND-JOIN-VETO-20261122-001A/.../check.py, plan(..., guard=True)): a proposed group of two or
more parents is dropped unless every distinction on every parent agrees with a transported reference
word.  Reference: the zero word under parity, the lexicographically first allowed word of the start under
not-all-equal; fresh reference values: the lexicographically first lawful completion of the reference
inputs.

Run (from the repository root):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --group source
"""

import argparse
from itertools import product
import json
import random
import time

import numpy as np
from pysat.solvers import Minisat22

import engine as E
import r1_holdings as R1

ARTIFACTS = R1.ARTIFACTS
SEED = 2026112305
VERSIONS = 64

# R2 horizons: (rounds, knot cap).  Chosen before running; long histories stop early (see deviations.md).
R2_HORIZON = {
    "seven_knot_source": (6, 300),
    "five_founder_clock": (16, 300),
    "explosive_00": (40, 1000),
    "explosive_04": (40, 1000),
    "explosive_13": (40, 1000),
}
R2_DEFAULT = (8, 300)


# ----------------------------------------------------------------------------------------------
# Lawful valued versions
# ----------------------------------------------------------------------------------------------

def sample_parity_words(stars, rng, count):
    names = sorted({d for r in stars for d in r})
    pos = {d: i for i, d in enumerate(names)}
    pivots = {}
    for row in stars:
        word = sum(1 << pos[d] for d in row)
        while word:
            top = word.bit_length() - 1
            if top in pivots:
                word ^= pivots[top]
            else:
                pivots[top] = word
                break
    out = []
    for _ in range(count):
        assigned = 0
        for b in range(len(names)):
            if b in pivots:
                bit = bin(pivots[b] & ~(1 << b) & assigned).count("1") & 1
            else:
                bit = rng.getrandbits(1)
            assigned |= bit << b
        out.append({d: (assigned >> pos[d]) & 1 for d in names})
    return out


def sample_nae_words(stars, rng, count, max_tries=400_000):
    """Uniform by rejection when the acceptance rate allows; otherwise Moser-Tardos resampling
    (each version lawful, distribution not exactly uniform).  Returns (words, method)."""
    names = sorted({d for r in stars for d in r})
    pos = {d: i for i, d in enumerate(names)}
    gen = np.random.default_rng(rng.getrandbits(64))
    rows = [np.array([pos[d] for d in row]) for row in stars]
    out, tries = [], 0
    while len(out) < count and tries < max_tries:
        batch = gen.integers(0, 2, size=(8192, len(names)), dtype=np.uint8)
        ok = np.ones(8192, dtype=bool)
        for r in rows:
            s_ = batch[:, r].sum(axis=1)
            ok &= (s_ > 0) & (s_ < len(r))
        tries += 8192
        for word in batch[ok]:
            out.append({d: int(word[pos[d]]) for d in names})
            if len(out) == count:
                break
    if len(out) == count:
        return out, "rejection (uniform)"
    out = []
    for _ in range(count):
        word = gen.integers(0, 2, size=len(names), dtype=np.uint8)
        while True:
            bad = [r for r in rows if 0 == word[r].sum() or word[r].sum() == len(r)]
            if not bad:
                break
            r = bad[int(gen.integers(len(bad)))]
            word[r] = gen.integers(0, 2, size=len(r), dtype=np.uint8)
        out.append({d: int(word[pos[d]]) for d in names})
    return out, "Moser-Tardos resampling (lawful, not uniform)"


SAMPLING_METHOD = {}


def valued_versions(stars, law, rng, count=VERSIONS, label=None):
    if law == "parity":
        words, method = sample_parity_words(stars, rng, count), "GF(2) linear algebra (uniform)"
    else:
        words, method = sample_nae_words(stars, rng, count)
    SAMPLING_METHOD[(label, law)] = method
    assert all(E.check_values(stars, w, law) for w in words)
    return words


def reference_word(stars, law):
    names = sorted({d for r in stars for d in r})
    if law == "parity":
        return {d: 0 for d in names}
    pos = {d: i + 1 for i, d in enumerate(names)}
    clauses = []
    for row in stars:
        clauses.append([pos[d] for d in row])
        clauses.append([-pos[d] for d in row])
    word = {}
    with Minisat22(bootstrap_with=clauses) as solver:
        assumptions = []
        for d in names:
            for bit in (0, 1):
                lit = -pos[d] if bit == 0 else pos[d]
                if solver.solve(assumptions=assumptions + [lit]):
                    word[d] = bit
                    assumptions.append(lit)
                    break
            else:
                raise AssertionError("no lawful reference word")
    assert E.check_values(stars, word, law)
    return word


# ----------------------------------------------------------------------------------------------
# Valued growth
# ----------------------------------------------------------------------------------------------

def first_lawful(law, inputs, count):
    for fresh in product((0, 1), repeat=count):
        if E.lawful_word(law, tuple(inputs) + fresh):
            return fresh
    raise AssertionError("no lawful completion")


def grow_valued(stars, values, law, rounds, knot_cap, rng, veto_reference=None):
    """Grow with values attached.  ``veto_reference`` switches the join veto on (the injected fault)."""
    frames = [tuple(tuple(r) for r in stars)]
    vals = dict(values)
    ref = dict(veto_reference) if veto_reference is not None else None
    statuses = []
    for _ in range(rounds):
        frame = frames[-1]
        room = None if knot_cap is None else knot_cap - len(frame)
        veto = None
        if ref is not None:
            veto = lambda group, frame=frame: any(vals[d] != ref[d] for p in group for d in frame[p])
        plan = E.plan_round(frame, law, veto, max_births=room)
        statuses.append(plan.status)
        if plan.status != "extend":
            break
        new_frame, births = E.apply_plan(frame, plan)
        for b in births:
            inputs = tuple(vals[d] for d in b.inputs)
            if len(b.fresh) == 0:
                assert E.lawful_word(law, inputs), "an implied birth must already be lawful"
            else:
                fresh = E.sample_completion(law, inputs, len(b.fresh), rng)
                for d, v in zip(b.fresh, fresh, strict=True):
                    vals[d] = v
            if ref is not None:
                rin = tuple(ref[d] for d in b.inputs)
                for d, v in zip(b.fresh, first_lawful(law, rin, len(b.fresh)) if b.fresh else (), strict=True):
                    ref[d] = v
        frames.append(new_frame)
    return frames, vals, statuses


# ----------------------------------------------------------------------------------------------
# The check
# ----------------------------------------------------------------------------------------------

def check_births(name, law, with_fault, versions=VERSIONS, horizon=None):
    rounds, cap = horizon or R2_HORIZON.get(name, R2_DEFAULT)
    stars = R1.start_for(name)
    reference = E.grow_history(stars, law, rounds, knot_cap=cap, cross_check=False)
    ref_reads = E.read_births(reference.frames)
    rng = random.Random(f"{SEED}:{name}:{law}")
    words = valued_versions(stars, law, rng, versions, label=name)
    veto_ref = reference_word(stars, law) if with_fault else None
    differing, first_round, lawful_end, stall_changed = 0, [], 0, 0
    for word in words:
        frames, vals, statuses = grow_valued(stars, word, law, rounds, cap, rng, veto_ref)
        reads = E.read_births(frames)
        if reads != ref_reads:
            differing += 1
            first_round.append(next((t + 1 for t, (a, b) in enumerate(zip(reads, ref_reads)) if a != b),
                                    min(len(reads), len(ref_reads)) + 1))
        stall_changed += statuses[-1:] != reference.statuses[-1:]
        lawful_end += E.check_values(frames[-1], vals, law)
    return {"history": name, "law": law, "fault": "join veto" if with_fault else "none", "versions": versions,
            "rounds": len(reference.frames) - 1, "knots_end": len(reference.frames[-1]),
            "births_total": sum(len(r) for r in ref_reads),
            "versions_with_different_births": differing,
            "versions_lawful_at_end": lawful_end,
            "earliest_difference_round_histogram": {str(k): first_round.count(k) for k in sorted(set(first_round))},
            "versions_with_different_final_status": stall_changed,
            "sampling": SAMPLING_METHOD.get((name, law))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", required=True, choices=sorted(R1.GROUPS))
    parser.add_argument("--fault", action="store_true", help="also run the engine with the join veto")
    parser.add_argument("--law", choices=E.LAWS)
    args = parser.parse_args()
    rows = []
    for name in R1.GROUPS[args.group]:
        for law in ([args.law] if args.law else E.LAWS):
            for fault in ((False, True) if args.fault else (False,)):
                t0 = time.time()
                row = check_births(name, law, fault)
                row["seconds"] = round(time.time() - t0, 1)
                rows.append(row)
                print(json.dumps(row, sort_keys=True), flush=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / f"r2_{args.group}{'_' + args.law if args.law else ''}{'_fault' if args.fault else ''}.json").write_text(
        json.dumps(rows, indent=1, sort_keys=True) + "\n")
    clean = [r for r in rows if r["fault"] == "none"]
    faulted = [r for r in rows if r["fault"] != "none"]
    print("clean versions differing:", sum(r["versions_with_different_births"] for r in clean),
          "| faulted rows flagged:", sum(r["versions_with_different_births"] > 0 for r in faulted), "of", len(faulted))


if __name__ == "__main__":
    main()

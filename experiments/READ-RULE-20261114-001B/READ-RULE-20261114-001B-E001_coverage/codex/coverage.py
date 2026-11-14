"""Frozen READ checks 1 and 2; authorized CARRY machinery is read in place.

No population inputs are copied and no source file is modified.  R1 uses the
existing CARRY syntactic traversal; r1_check.py is an independent raw-key path.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
if str(CARRY) not in sys.path:
    sys.path.append(str(CARRY))
import inputs
import window
from scope import SyntaxPreparation


def read_raw(index_row):
    """Seek to a single original JSON line rather than materialize 3.5 GB."""
    source = CARRY / "window_full/results.jsonl"
    with source.open("rb") as stream:
        stream.seek(index_row["offset"])
        line = stream.read(index_row["bytes"])
    record = json.loads(line)
    if record["case"] != index_row["key"]:
        raise ValueError("source offset/key no longer agrees")
    return record


def syntax(key):
    prep = SyntaxPreparation(key)
    data = window.pendant_data(prep)
    carried = window.carried_sequence(prep, data)
    pendant = set(data["pendant"])
    candidates = set()
    for args in data["knots"]:
        if len(set(args)) != 3:
            continue
        for k in args:
            if k >= 3:
                continue
            for x in args:
                if x < 3:
                    continue
                z, = set(args) - {k, x}
                candidates.add((k, x, z))
    candidates = sorted(candidates)
    r1_witnesses = [item for item in candidates if item[2] in pendant]
    r1_positions = {item[0] for item in r1_witnesses}
    phases = []
    t, period = carried["preperiod"], carried["period"]
    for phase, mask in enumerate(carried["masks"][t:]):
        witnesses = [list(w) for w in r1_witnesses if mask >> w[0] & 1]
        phases.append(dict(residue=phase, s_mod_period=(t + phase) % period,
                           carried_mask=mask, covered=bool(witnesses), witnesses=witnesses))
    flags = [row["covered"] for row in phases]
    return prep, dict(carried=carried, candidates=[list(c) for c in candidates],
                      r1=dict(all_residues=all(flags), some_residues=any(flags),
                              some_residues_only=any(flags) and not all(flags),
                              positions=sorted(r1_positions), residues=phases),
                      syntactic=data)


def conjunction(values):
    values = list(values)
    return False if False in values else None if None in values else True


def _q_states(raw, prep, checkpoint):
    recorded = raw["window"]
    if not recorded.get("complete"):
        return None
    args = [list(a) for c, a in prep.flat(prep.S)["calls"] if c == prep.S]
    if len(args) != len(raw["R_i"]):
        raise ValueError("SELF argument / relation count differs")
    calls = [dict(arguments=a, relation=int(r, 16)) for a, r in zip(args, raw["R_i"])]
    current = frozenset((int(row["J"], 16), tuple(row["partition"]))
                        for row in recorded["starts"])
    seen, phases = {}, []
    state_bonds = {(int(row["J"], 16), tuple(row["partition"])): row
                   for row in recorded["state_bonds"]}
    for depth, level in enumerate(recorded["levels"]):
        if current in seen:
            raise ValueError("Q_s repeated before recorded repeat")
        seen[current] = depth
        if len(current) != level["states"]:
            raise ValueError("reconstructed Q_s cardinality disagrees")
        if not current.issubset(state_bonds):
            raise ValueError("reconstructed Q_s contains an unrecorded state")
        minimum = min((state_bonds[q]["g"] for q in current
                       if isinstance(state_bonds[q]["g"], int)), default="> 6")
        if minimum != level["U"]:
            raise ValueError("reconstructed Q_s window minimum disagrees")
        if depth >= recorded["preperiod"]:
            phases.append(current)
        current = frozenset(window.step(q, call, prep.k) for q in current for call in calls)
        checkpoint()
    if current not in seen or seen[current] != recorded["preperiod"]:
        raise ValueError("reconstructed Q_s repeat disagrees")
    if len(phases) != recorded["period"]:
        raise ValueError("reconstructed phase count disagrees with period")
    return phases


def _ties(projection, p, x, z):
    labels = {label: bit for bit, label in enumerate(projection["labels"])}
    rows = projection["allowed"]
    if not rows:
        raise ValueError("empty window cannot define a tie")
    def values(left, right):
        return {((row >> labels[left]) & 1) + 2 * ((row >> labels[right]) & 1)
                for row in rows}
    px = values(p, x)
    px_tied = px in ({0, 3}, {1, 2})
    px_free = px == {0, 1, 2, 3}
    if not (px_tied or px_free):
        raise ValueError("pair is neither a complement-closed tie nor free")
    zp_opposite = values(z, p) == {1, 2}
    zx_opposite = values(z, x) == {1, 2}
    return ("equal" if px == {0, 3} else "opposite" if px_tied else "free",
            zp_opposite, zx_opposite, px_free and (zp_opposite or zx_opposite))


def semantic_coverage(raw, prep, syn, checkpoint=lambda: None):
    """Retain exact state-wise ties; do not choose disputed quantifiers.

    The specification fixes a knot before "every state".  It does not say how
    a state in which its position is not carried participates.  Both literal
    all-Q and carried-Q predicates are retained, and affected flags are null.
    """
    recorded = raw["window"]
    candidates = [tuple(c) for c in syn["candidates"]]
    sequence = syn["carried"]
    tR, pR = sequence["preperiod"], sequence["period"]
    if not recorded.get("complete"):
        absent = not any(any(mask >> k & 1 for k, _, _ in candidates)
                         for mask in sequence["masks"][tR:])
        return dict(complete=absent, window_complete=False,
                    all_residues=False if absent else None,
                    some_residues=False if absent else None,
                    q1_exception_only=False if absent else None,
                    residues=[], state_ties=[], ambiguities=[],
                    skipped=None if absent else "repeating Q_s is capped/incomplete",
                    gate_R=dict(complete=absent, passed=True if absent else None,
                                violations=[]),
                    gate_R1=dict(complete=not any(r["covered"] for r in syn["r1"]["residues"]),
                                 passed=True if not any(r["covered"] for r in syn["r1"]["residues"]) else None,
                                 violations=[]))
    qphases = _q_states(raw, prep, checkpoint)
    tQ, pQ = recorded["preperiod"], recorded["period"]
    for q, states in enumerate(qphases):
        depth = tQ + q
        mask_index = depth if depth < len(sequence["masks"]) else tR + (depth - tR) % pR
        actual_mask = 0
        for state in states:
            actual_mask |= sum(1 << k for k in range(3) if state[1][prep.k + k] < prep.k)
        if actual_mask != sequence["masks"][mask_index]:
            raise ValueError("reconstructed Q_s union of carried positions differs from R_s")
    # Align asymptotic congruences; no arbitrary phase origin is selected.
    gcd = math.gcd(pR, pQ)
    r_to_q = [[q for q in range(pQ) if (tQ + q - tR - r) % gcd == 0]
              for r in range(pR)]
    repeated_states = sorted(set().union(*qphases))
    carried_candidates = any(any(state[1][prep.k + k] < prep.k for k, _, _ in candidates)
                             for state in repeated_states)
    body = None
    actual_prep = None
    if carried_candidates:
        actual_prep = inputs.load_paths().Preparation(json.loads(raw["key"]))
        body = window.body_allowed(actual_prep, actual_prep.S)
    state_id = {q: j for j, q in enumerate(repeated_states)}
    state_rows, analyses = [], {}
    for q in repeated_states:
        available = [j for j, (k, _, _) in enumerate(candidates) if q[1][prep.k + k] < prep.k]
        projection = window.project_state(actual_prep, q, body) if available else None
        entries = []
        per_candidate = {}
        for j in available:
            k, x, z = candidates[j]
            aliases = projection["end_aliases"]
            tie = _ties(projection, aliases[k], aliases[x], aliases[z])
            per_candidate[j] = tie
            entries.append([j, aliases[k], tie[0], int(tie[1]), int(tie[2]), int(tie[3])])
        analyses[q] = per_candidate
        state_rows.append(dict(id=state_id[q], J=hex(q[0]), partition=list(q[1]), ties=entries))
        checkpoint()
    residues, ambiguities = [], []
    r_violations, r_disputed, r1_violations = [], [], []
    for phase, qindices in enumerate(r_to_q):
        states = set().union(*(qphases[q] for q in qindices))
        summaries = []
        for j, (k, x, z) in enumerate(candidates):
            codes = [analyses[q][j] for q in states if j in analyses[q]]
            if not codes:
                continue
            exceptions = sum(code[3] for code in codes)
            survives = len(codes) - exceptions
            histogram = Counter((code[0], int(code[1]), int(code[2]), int(code[3])) for code in codes)
            summaries.append(dict(candidate=j, k=k, x=x, z=z, carried_states=len(codes),
                                   not_carried_states=len(states) - len(codes),
                                   exception_states=exceptions, surviving_states=survives,
                                   all_Q_survive=len(codes) == len(states) and exceptions == 0,
                                   all_carried_Q_survive=exceptions == 0,
                                   tie_histogram=[[list(code), count] for code, count in sorted(histogram.items())]))
        strict = any(row["all_Q_survive"] for row in summaries)
        carried_only = any(row["all_carried_Q_survive"] for row in summaries)
        flag = strict if strict == carried_only else None
        if flag is None:
            ambiguities.append(dict(kind="every_state_when_not_carried", residue=phase,
                                    question="Does 'every state' include Q states in which this knot's position is not carried, or only those in which it is carried?"))
        killed_everywhere = bool(summaries) and all(row["surviving_states"] == 0 for row in summaries)
        killed_somewhere_each = bool(summaries) and all(row["exception_states"] > 0 for row in summaries)
        q1 = killed_everywhere if killed_everywhere == killed_somewhere_each else None
        if q1 is None:
            ambiguities.append(dict(kind="exception_quantifier", residue=phase,
                                    question="For Q1, must each reading meet the exception in every carried Q state, or does meeting it in some carried Q state suffice?"))
        r1 = syn["r1"]["residues"][phase]["covered"]
        U = [recorded["residues"][q]["U"] for q in qindices]
        violations = [q for q, u in zip(qindices, U) if not isinstance(u, int) or u > 3]
        if strict and violations:
            r_violations.append(dict(R_residue=phase, Q_residues=violations))
        elif carried_only and violations:
            r_disputed.append(dict(R_residue=phase, Q_residues=violations))
        if r1 and violations:
            r1_violations.append(dict(R_residue=phase, Q_residues=violations))
        residues.append(dict(residue=phase, s_mod_period=(tR + phase) % pR,
                             Q_residues=qindices, state_ids=sorted(state_id[q] for q in states),
                             U=U, knots=summaries, applies=flag,
                             all_Q_applies=strict, carried_Q_applies=carried_only,
                             any_state_survives=any(row["surviving_states"] for row in summaries),
                             exception_only=q1, killed_in_every_carried_Q=killed_everywhere,
                             each_knot_killed_in_some_carried_Q=killed_somewhere_each,
                             R1_covered=r1))
    flags = [row["applies"] for row in residues]
    q1flags = [row["exception_only"] for row in residues]
    return dict(complete=True, window_complete=True, all_residues=conjunction(flags),
                some_residues=True if True in flags else None if None in flags else False,
                q1_exception_only=True if True in q1flags else None if None in q1flags else False,
                candidates=syn["candidates"], residues=residues, state_ties=state_rows,
                ambiguities=ambiguities, Q_preperiod=tQ, Q_period=pQ,
                gate_R=dict(complete=not r_disputed,
                            passed=False if r_violations else None if r_disputed else True,
                            basis="checked larger carried-state interpretation too; no quantifier choice",
                            violations=r_violations, interpretation_dependent_violations=r_disputed),
                gate_R1=dict(complete=True, passed=not r1_violations, violations=r1_violations))


def run_family(index_row, *, semantic=True, conditional=True, checkpoint=lambda: None):
    started = time.monotonic()
    key = index_row["key"]
    prep, syn = syntax(key)
    result = dict(key=key, key_sha256=hashlib.sha256(key.encode()).hexdigest(),
                  in_scope=index_row["in_scope"], stratum=index_row["stratum"],
                  verdict=index_row["verdict"], weight=index_row["weight"],
                  R1=syn["r1"], carried=syn["carried"], candidates=syn["candidates"])
    if semantic or conditional:
        record = read_raw(index_row)
        if record["status"] != "ok":
            result["error"] = "source latest record is not ok"
            return result
        raw = record["result"]
        if semantic:
            result["R"] = semantic_coverage(raw, prep, syn, checkpoint)
        if conditional:
            from conditional import conditional_from_calls
            arguments = [list(a) for c, a in prep.flat(prep.S)["calls"] if c == prep.S]
            if len(arguments) != len(raw["R_i"]):
                raise ValueError("R_i count mismatch")
            result["conditional"] = conditional_from_calls(
                [dict(arguments=a, relation=int(r, 16)) for a, r in zip(arguments, raw["R_i"])],
                checkpoint)
    result["seconds"] = time.monotonic() - started
    return result

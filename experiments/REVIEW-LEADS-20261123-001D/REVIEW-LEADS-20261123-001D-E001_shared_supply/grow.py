"""Grow the joint starts under the guarded rule and the recompute-after-every-birth rule, with exhaustive branching at the
births contested at the shared donor. Run from the repository root after `gate.py 1`, `addendum.py` and `gate.py 2`:

    timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> [start ...]
"""
from collections import Counter, defaultdict
import json
import sys
import time

import engine
import lib

ART = lib.ARTIFACTS
NAMES = ("X", "Y")


def check_addendum():
    sha = (ART / "construction_addendum.sha256").read_text().splitlines()[0].split()[0]
    assert sha == lib.file_sha256(lib.HERE / "construction_addendum.md"), "addendum changed after hashing"
    gate2 = json.loads((ART / "gate2.json").read_text())
    assert gate2["addendum_sha256"] == sha and gate2["gate2_ok_for_every_start"], "gate 2 not passed"
    return sha


def needed_donor_proposals(joint):
    """Proposals through the donor that are roles of a registered tick: key -> [(source, tick age)]."""
    out = defaultdict(list)
    for i, src in enumerate(joint.srcs):
        m = joint.maps[i]
        for age in src.future_ticks():
            for r in src.needed(age):
                if r < len(src.stars):
                    continue
                ps = src.roles[r][0]
                if all(p < len(src.stars) for p in ps):
                    key = tuple(sorted(m[p] for p in ps))
                    if joint.donor in key:
                        out[key].append((NAMES[i], age))
    return out


def describe(joint, key):
    kinds = {joint.origin[k] for k in key if k != joint.donor}
    return "unary" if len(key) == 1 else "X" if kinds <= {"X"} else "Y" if kinds <= {"Y"} else "cross"


def cert_label(joint, c):
    if c is None:
        return None
    if c["kind"] == "exhausted_parent":
        return {"kind": c["kind"], "parent_knot": c["parent_knot"], "parent_is_donor": c["parent_knot"] == joint.donor,
                "unmade_role_parents": c["role_parents_present"], "spending_event": c["spending_event"],
                "spending_birth_parents": c["spending_birth"]}
    return c


def guarded_row(joint):
    st, rec = lib.run_guarded(joint)
    row = {"births": rec["births"], "steps_completed": len(rec["steps"]), "cap": rec["cap"], "stall": rec["stall"],
           "ticks": {}}
    for i, src in enumerate(joint.srcs):
        for age in src.future_ticks():
            key = f"{NAMES[i]} tick {age}"
            if (i, age) in rec["ticks"]:
                row["ticks"][key] = {"status": "made", **rec["ticks"][(i, age)]}
            elif rec["stall"]:
                row["ticks"][key] = {"status": "stalled", "at_step": rec["stall"]["step"],
                                     "shortages": rec["stall"]["shortages"]}
            else:
                cert = st.lost(i, age)
                if cert is not None:
                    row["ticks"][key] = {"status": "lost", "certificate": cert_label(joint, cert)}
                else:
                    row["ticks"][key] = {"status": "not reached within the caps"}
    return row


def recompute_rows(joint, policy, strict=False):
    start = lib.State(joint)
    init_props = lib.donor_proposals(start, policy)
    needed = needed_donor_proposals(joint)
    t0 = time.time()
    leaves, nodes = (lib.strict_contest_leaves if strict else lib.contest_leaves)(joint, policy)
    total_ways = sum(w for _, w, _ in leaves.values())
    sampled = len(leaves) > lib.MAX_BRANCHES
    tally_ways, tally_leaves, tally_fine = Counter(), Counter(), Counter()
    cert_ways = Counter()
    examples = {}
    starved_ways = Counter()
    for key, (leaf, ways, example) in leaves.items():
        out, fair_written = lib.classify_leaf(leaf, policy)
        coarse = tuple("lost" if any(e["status"] == "lost" for e in row.values()) else "keeps" for row in out)
        fine = tuple("/".join(f"t{a}:{e['status']}" for a, e in row.items()) for row in out)
        label = f"X {coarse[0]}, Y {coarse[1]}"
        tally_ways[label] += ways
        tally_leaves[label] += 1
        fine_label = f"X [{fine[0]}], Y [{fine[1]}]"
        tally_fine[fine_label] += ways
        made = {tuple(p[0]) for p in leaf.P.log if joint.donor in p[0]}
        made |= {tuple(c) for c in fair_written if joint.donor in c}
        starved = [p for p in init_props if tuple(p) not in made]
        desc = tuple(sorted((describe(joint, p), tuple(p), tuple(needed.get(tuple(p), []))) for p in starved))
        starved_ways[desc] += ways
        for i, row in enumerate(out):
            for age, e in row.items():
                if e["status"] == "lost":
                    c = cert_label(joint, e["certificate"])
                    ck = json.dumps({"source": NAMES[i], "tick": age, **{k: c[k] for k in c if k != "spending_event"}},
                                    sort_keys=True)
                    cert_ways[ck] += ways
        if label not in examples:
            examples[label] = {"choice_sequence": [list(map(int, p)) for p in example],
                               "classification": [{str(a): {k: v for k, v in e.items() if k != "certificate"}
                                                   for a, e in row.items()} for row in out],
                               "certificates": [{str(a): cert_label(joint, e["certificate"]) for a, e in row.items()
                                                 if e["status"] == "lost"} for row in out]}
    return {"policy": policy, "donor_loose": start.P.loose[joint.donor], "enabled_proposals_through_donor":
            [{"parents": list(map(int, p)), "side": describe(joint, p), "role_of": needed.get(tuple(p), [])}
             for p in init_props], "contested_at_start": len(init_props) > start.P.loose[joint.donor],
            "choice_sequences": total_ways, "distinct_leaves": len(leaves), "tree_states_expanded": nodes,
            "sampled": sampled, "outcome_by_choice_sequences": dict(tally_ways),
            "outcome_by_distinct_leaves": dict(tally_leaves),
            "outcome_by_choice_sequences_by_tick": dict(tally_fine),
            "starved_proposals_by_choice_sequences": [{"starved": [[s[0], list(s[1]), s[2]] for s in k], "choice_sequences": v}
                                                      for k, v in sorted(starved_ways.items(), key=lambda kv: -kv[1])],
            "certificates_by_choice_sequences": [{"certificate": json.loads(k), "choice_sequences": v}
                                                 for k, v in sorted(cert_ways.items())],
            "examples": examples, "seconds": round(time.time() - t0, 1)}


def main(names, strict=False):
    sha = check_addendum()
    from addendum import SPECS
    S = lib.ring_sources()
    result = {"addendum_sha256": sha, "starts": {}}
    for name, label, xk, yk, needs_repair in SPECS:
        if names and name not in names:
            continue
        X, Y = S[xk], S[yk]
        repair = {}
        if needs_repair:
            unfunded = lib.merge(name, X, Y, 0)
            _, _, _, sc = engine.ordinary_layer(engine.Pres.from_stars(unfunded.stars))
            repair = {int(k): int(n) for k, n in sc}
        entry = {"class": label, "x": xk, "y": yk}
        for s in (0, 1):
            j = lib.merge(f"{name}-s{s}", X, Y, s, repair)
            cell = {"donor": j.donor, "donor_loose": engine.Pres.from_stars(j.stars).loose[j.donor]}
            cell["guarded"] = guarded_row(j)
            cell["recompute"] = {}
            for policy in lib.POLICIES:
                cell["recompute"][policy] = recompute_rows(j, policy, strict)
                print(name, s, policy, cell["recompute"][policy]["choice_sequences"],
                      cell["recompute"][policy]["outcome_by_choice_sequences"],
                      cell["recompute"][policy]["seconds"], flush=True)
            entry[f"s{s}"] = cell
        result["starts"][name] = entry
        (ART / (f"grow_strict_{name}.json" if strict else f"grow_{name}.json")).write_text(json.dumps({"addendum_sha256": sha, name: entry}, indent=1,
                                                          sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(set(args), strict="--strict" in sys.argv)

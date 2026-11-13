"""Exact exploratory ray/side-branch comparison; never reads BOND-DEPTH data.

Run from the repository root with .venv/bin/python -B <this file>.
Unexpanded SELF calls receive the greatest fixed point, not a free boundary.
Only one-definition, three-port, non-pass-through corpus families are used.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "artifacts/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches"
SOURCE = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"


def image(definition, old):
    k, locals_, calls = definition
    result = 0
    for state in range(1 << (k + locals_)):
        for callee, args in calls:
            sub = sum(((state >> v) & 1) << j for j, v in enumerate(args))
            if not ((126 if callee == "K" else old) >> sub) & 1:
                break
        else:
            result |= 1 << (state & 7)
    return result


def fixed_point(definition):
    history = [255]
    while (new := image(definition, history[-1])) != history[-1]:
        assert new & history[-1] == new
        history.append(new)
    return new, history


def corpus():
    rows = []
    for file in sorted(SOURCE.glob("sample_*.jsonl.gz")):
        for line, raw in enumerate(gzip.open(file, "rt"), 1):
            row = json.loads(raw)
            if not row.get("limit_only") or len(row["defs"]) != 1:
                continue
            definition = row["defs"][0]
            selfs = [a for cl, a in definition[2] if cl == "SELF"]
            if len(selfs) < 2 or any(set(a) == {0, 1, 2} for a in selfs):
                continue
            rows.append(dict(file=str(file.relative_to(ROOT)), line=line,
                             definition=definition, first_dead=row["first_dead"]))
    rows.sort(key=lambda r: (r["definition"][1], len(r["definition"][2]),
                             r["file"], r["line"]))
    return rows


def cut(definition, depth, side=None):
    """Expand ray copies 0..depth, optionally one non-ray child (level,index).

    SELF index is its ordinal among SELF calls in body order. Fresh local
    identity is (copy path, local index); all shared actual names are retained.
    """
    gfp, history = fixed_point(definition)
    locals_ = definition[1]
    expanded = {tuple([0] * j) for j in range(depth + 1)}
    if side is not None:
        level, index = side
        expanded.add(tuple([0] * level + [index]))
    names = ["a", "b", "c"]
    factors = []
    copies = {}
    def visit(path, ports):
        own = list(range(len(names), len(names) + locals_))
        names.extend(f"{'r' if not path else '.'.join(map(str,path))}:x{j}" for j in range(locals_))
        env = list(ports) + own
        copies[path] = dict(ports=list(ports), own=own)
        self_index = 0
        for callee, args in definition[2]:
            actual = [env[j] for j in args]
            if callee == "K":
                factors.append((actual, 126))
            else:
                child = path + (self_index,)
                self_index += 1
                if child in expanded:
                    visit(child, actual)
                else:
                    factors.append((actual, gfp))
    visit((), [0, 1, 2])
    ray = sorted({0, 1, 2} | {v for p, c in copies.items() if all(j == 0 for j in p) for v in c["own"]})
    target = copies[tuple([0] * depth)]["own"]
    assert len(names) <= 23, "enumeration resource ceiling"
    states = np.arange(1 << len(names), dtype=np.uint32)
    ok = np.ones(len(states), dtype=bool)
    for variables, relation in factors:
        indices = sum(((states >> v) & 1) << j for j, v in enumerate(variables))
        ok &= ((relation >> indices) & 1).astype(bool)
    return dict(names=names, factors=factors, ray=ray, target=target,
                states=states[ok], gfp=gfp, gfp_history=history,
                expanded_paths=[list(p) for p in sorted(expanded)])


def projection(states, support):
    codes = sum(((states >> v) & 1) << j for j, v in enumerate(support))
    return sorted(map(int, np.unique(codes)))


def bond(states, support, cache):
    key = tuple(sorted(support))
    if key not in cache:
        cache[key] = projection(states, key)
    if not cache[key] or len(cache[key]) == 1 << len(key):
        return False
    for j in range(len(key)):
        smaller = key[:j] + key[j+1:]
        if smaller not in cache:
            cache[smaller] = projection(states, smaller)
        if len(cache[smaller]) != 1 << len(smaller):
            return False
    return True


def least(states, pool, endpoints, maximum=None):
    cache = {}
    extras = [v for v in pool if v not in endpoints]
    searched = []
    for size in range(2, min(maximum or len(pool), len(pool)) + 1):
        for extra in it.combinations(extras, size - 2):
            support = tuple(sorted((*endpoints, *extra)))
            verdict = bond(states, support, cache)
            searched.append(dict(support=list(support), is_bond=verdict,
                                 allowed=cache[support]))
            if verdict:
                return support, searched
    return None, searched


def incidence_forest(cut_):
    """For a TOP frontier, test acyclicity of the actual NAE incidence graph."""
    if cut_["gfp"] != 255:
        return False
    knots = [variables for variables, relation in cut_["factors"] if relation != 255]
    parent = list(range(len(cut_["names"]) + len(knots)))
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for j, variables in enumerate(knots, len(cut_["names"])):
        for v in variables:
            a,b = find(j),find(v)
            if a == b:
                return False
            parent[a] = b
    return True


def search(require_acyclic=False):
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    rows = corpus()
    attempts = []
    # Smallest genuine branching limit-only descriptions first. A strict
    # same-pair shortcut is the declared stop, not a distributional census.
    for row in rows:
        definition = row["definition"]
        if definition[1] > 3:
            break
        selfs = sum(cl == "SELF" for cl, _ in definition[2])
        for depth in (1, 2, 3):
            if 3 + (depth + 2) * definition[1] > 20:
                continue
            ray_cut = cut(definition, depth)
            if require_acyclic and not incidence_forest(ray_cut):
                attempts.append(dict(file=row["file"],line=row["line"],depth=depth,
                                     excluded="ray incidence has a cycle or non-TOP frontier"))
                break
            pair_rays = {}
            for u, v in it.product(range(3), ray_cut["target"]):
                support, exclusions = least(ray_cut["states"], ray_cut["ray"], (u, v))
                pair_rays[u, v] = (support, exclusions)
            family_ray_min = min((len(s) for s, _ in pair_rays.values() if s is not None), default=None)
            for level, side_index in it.product(range(depth + 1), range(1, selfs)):
                branch_cut = cut(definition, depth, (level, side_index))
                # IDs vary when a side copy is inserted before later ray
                # copies; match endpoints and ray pools by identity names.
                name_id = {name: j for j, name in enumerate(branch_cut["names"])}
                for (u, vr), (ray_support, exclusions) in pair_rays.items():
                    if ray_support is None or len(ray_support) <= 3:
                        continue
                    v = name_id[ray_cut["names"][vr]]
                    branch_support, candidates = least(branch_cut["states"], range(len(branch_cut["names"])), (u, v), 3)
                    if branch_support is None:
                        continue
                    result = dict(source=row, depth=depth, side=[level, side_index],
                                  endpoints=[ray_cut["names"][u], ray_cut["names"][vr]],
                                  ray_support=None if ray_support is None else [ray_cut["names"][j] for j in ray_support],
                                  ray_minimum=None if ray_support is None else len(ray_support),
                                  global_support=[branch_cut["names"][j] for j in branch_support],
                                  global_minimum=len(branch_support), family_ray_minimum=family_ray_min,
                                  ray_incidence_forest=incidence_forest(ray_cut),
                                  ray_cut={k:v for k,v in ray_cut.items() if k != "states"},
                                  branch_cut={k:v for k,v in branch_cut.items() if k != "states"},
                                  ray_allowed_assignments=list(map(int,ray_cut["states"])),
                                  branch_allowed_assignments=list(map(int,branch_cut["states"])),
                                  ray_support_search=exclusions,
                                  prior_attempts=attempts,
                                  eligible_families=len(rows), elapsed_seconds=time.monotonic()-start,
                                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                    filename = "witness_acyclic.json" if require_acyclic else "witness.json"
                    (OUT/filename).write_text(json.dumps(result, indent=2)+"\n")
                    print(json.dumps({k:v for k,v in result.items() if k not in ("ray_cut","branch_cut","ray_allowed_assignments","branch_allowed_assignments","ray_support_search","prior_attempts")},indent=2))
                    return result
            attempts.append(dict(file=row["file"],line=row["line"],depth=depth,
                                 ray_variables=len(ray_cut["ray"]), family_ray_minimum=family_ray_min,
                                 seconds=time.monotonic()-start))
            print(json.dumps(attempts[-1]), flush=True)
    filename = "no_acyclic_witness.json" if require_acyclic else "no_witness.json"
    (OUT/filename).write_text(json.dumps(dict(attempts=attempts,elapsed_seconds=time.monotonic()-start),indent=2)+"\n")
    return None


if __name__ == "__main__":
    search(require_acyclic="--acyclic" in sys.argv)

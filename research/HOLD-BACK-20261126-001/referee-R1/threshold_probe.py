"""Run the fixed pair draws in [start, stop). Emit one JSON object per pair.

Usage from the repository root:
    .venv/bin/python -B research/HOLD-BACK-20261126-001/referee-R1/threshold_probe.py 0 1
"""

import argparse
import gzip
import json
import random
import resource
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

MEMORY = 2 * 1024**3
resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
RESEARCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESEARCH / "SWITCH-RECEIVERS-20261126-001"))
import receivers

engine = receivers.eng
catalogue = receivers.bench
MARK_ROUNDS = (3, 5, 8)
ROUNDS = 24
BOUND = 6000
RECEIVER = "receiver-holding-one-two-two"


def local_fresh(p, demand):
    return max(3 - p, 1, min(demand, p + 1))


def cap_fresh(p, demand):
    return min(3, max(demand, 3 - p, 1))


class Reading(engine.Law):
    def __init__(self, mode):
        super().__init__("ORD", "CANCEL-WAIT", None, "nae")
        self.give = {"local": local_fresh, "cap": cap_fresh}[mode]

    def fresh(self, kind, p, D, o):
        return self.give(p, D)


class Names:
    """Exact shared dictionary of descent descriptions within a pair of starts."""

    def __init__(self):
        self.entries = {}

    def get(self, description):
        return self.entries.setdefault(description, len(self.entries))


class History:
    def __init__(self, state, roles, names):
        self.state = state
        self.roles = roles
        self.names = names

    def fork(self):
        return History(self.state.copy(), self.roles.copy(), self.names.copy())


def initial(stars, roles, pool):
    name_counts = Counter()
    names = []
    for role in roles:
        names.append(pool.get(("start", role, name_counts[role])))
        name_counts[role] += 1
    return History(engine.from_stars(stars), [frozenset([r]) for r in roles], names)


def next_round(history, law, guard, pool):
    """Use the shared round, reading births directly rather than using archived digests."""
    state = history.state.copy()
    record = engine.play_round(state, law, guard)
    history.state = state
    siblings = Counter()
    decisions = Counter()
    own = []
    for birth in record["births"]:
        parents = birth["parents"]
        role = frozenset.union(*(history.roles[u] for u in parents))
        key = (birth["kind"], tuple(sorted(history.names[u] for u in parents)))
        name = pool.get((*key, siblings[key]))
        siblings[key] += 1
        assert birth["id"] == len(history.names)
        history.names.append(name)
        history.roles.append(role)
        p, demand = birth["p"], birth["D"]
        given = birth["f"]
        assert given == law.give(p, demand)
        decisions[(birth["kind"], p, demand, "+".join(sorted(role)))] += 1
        if role == {"A"}:
            own.append((name, given, len(state.places[birth["id"]])))
    return {"own": sorted(own), "births": len(record["births"]), "decisions": decisions}


def reach(st, starts):
    """Minimum number of shared distinctions from any start in the given set."""
    distance = dict.fromkeys(starts, 0)
    queue = deque(distance)
    while queue:
        u = queue.popleft()
        for v in st.meets(u):
            if v not in distance:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def read_members(history, select):
    """Joinable members meet the same other knot. Direct sharing links their parts."""
    st, roles = history.state, history.roles
    members = [u for u, h, k in engine.live_members(st)]
    home = [u for u in members if roles[u] == {"A"}]
    far = [u for u in members if roles[u] == {"B"}]
    if not home or not far:
        return None, []
    by_witness = defaultdict(list)
    around = {}
    for u in members:
        around[u] = {u} | st.meets(u)
        for v in around[u]:
            by_witness[v].append(u)
    linked = set(home)
    queue = deque(linked)
    seen = set()
    while queue:
        u = queue.popleft()
        for witness in around[u] - seen:
            seen.add(witness)
            for v in by_witness[witness]:
                if v not in linked:
                    linked.add(v)
                    queue.append(v)
    has_link = any(u in linked for u in far)
    if not select:
        return has_link, []
    distance = reach(st, (u for u in range(st.n_knots) if roles[u] == {"A"}))
    ordered = sorted(far, key=lambda u: (distance.get(u, float("inf")), u))
    selected = []
    for wanted, limit in ((True, 5), (False, 2)):
        subset = [u for u in ordered if (u in linked) == wanted]
        for u in subset[:limit]:
            selected.append({"linked": wanted, "knot": u, "name": history.names[u],
                             "sharings": distance.get(u)})
    return has_link, selected


def grow(history, law, pool, checkpoints=False):
    guard = engine.Guard(4)
    rows, snapshots, links = [], {}, []
    stop = "rounds"
    while history.state.round < ROUNDS:
        try:
            row = next_round(history, law, guard, pool)
        except engine.GuardStop as exc:
            stop = "guard/" + exc.what
            break
        rows.append(row)
        if checkpoints:
            at = history.state.round
            linked, targets = read_members(history, at in MARK_ROUNDS)
            links.append(linked)
            if at in MARK_ROUNDS:
                snapshots[at] = (history.fork(), targets)
        if history.state.n_knots > BOUND:
            stop = "knots"
            break
    return rows, snapshots, links, stop


def change(history, u):
    st = history.state
    d = st.n_distinctions
    st.places[u].append(d)
    st.holders.append([u])
    st.barred.append(False)
    st.maker.append(u)


def overlap(rows):
    counts = Counter()
    for row in rows:
        counts.update(row["decisions"])
    return [[kind, p, d, role, local_fresh(p, d), cap_fresh(p, d), n]
            for (kind, p, d, role), n in sorted(counts.items())]


def by_round(rows):
    return [[sum(row["decisions"].values()),
             sum(n for (kind, p, d, role), n in row["decisions"].items()
                 if local_fresh(p, d) != cap_fresh(p, d))]
            for row in rows]


def read_pair(stars, roles, mode, pool):
    law = Reading(mode)
    base, snapshots, links, stop = grow(initial(stars, roles, pool), law, pool, True)
    result = {"law": mode, "linked": links, "base_end": stop, "base_horizon": len(base),
              "base_births": [r["births"] for r in base], "base_overlap": overlap(base),
              "base_decisions_by_round": by_round(base), "changes": []}
    for at, (snapshot, targets) in snapshots.items():
        if at >= len(base):
            continue
        for target in targets:
            altered = snapshot.fork()
            change(altered, target["knot"])
            marked, _, _, end = grow(altered, law, pool)
            shared = min(len(base) - at, len(marked))
            different = next((i for i in range(shared) if base[at+i]["own"] != marked[i]["own"]), None)
            heard = None if different is None else at + different + 1
            row = {**target, "after": at, "heard": heard, "common_horizon": at + shared,
                   "marked_horizon": at + len(marked), "marked_end": end,
                   "marked_suffix_overlap": overlap(marked), "suffix_decisions_by_round": by_round(marked)}
            if heard is not None:
                old, new = Counter(base[heard-1]["own"]), Counter(marked[different]["own"])
                row["missing_from_marked"] = sorted((old-new).elements())
                row["added_in_marked"] = sorted((new-old).elements())
                row["later_births_common"] = [sum(r["births"] for r in base[heard:at+shared]),
                                              sum(r["births"] for r in marked[different+1:shared])]
                row["later_births"] = [sum(r["births"] for r in base[heard:]),
                                       sum(r["births"] for r in marked[different+1:])]
            result["changes"].append(row)
    return result


def main():
    args = argparse.ArgumentParser()
    args.add_argument("start", type=int)
    args.add_argument("stop", type=int)
    indices = args.parse_args()
    assert 0 <= indices.start < indices.stop <= 4
    source = RESEARCH / "HOLD-BACK-20261126-001" / "linked_runs.jsonl.gz"
    with gzip.open(source, "rt") as lines:
        roster = sorted({json.loads(line)["B"] for line in lines})
    assert len(roster) == 28
    sample = random.Random(2026112603).sample(roster, 4)
    receivers.register()
    catalogue.STARS[RECEIVER] = [[0, 1, 3], [0, 2, 4, 5], [1, 2, 6, 7]]
    catalogue.SITE[RECEIVER] = 0
    for i in range(indices.start, indices.stop):
        cpu, wall = time.process_time(), time.monotonic()
        far = sample[i]
        stars, roles = catalogue.build(RECEIVER, far, 3, join="meeting")
        pool = Names()
        arms = {mode: read_pair(stars, roles, mode, pool) for mode in ("local", "cap")}
        result = {"draw": i + 1, "far": far, "arms": arms,
                  "cpu_seconds": round(time.process_time()-cpu, 4),
                  "wall_seconds": round(time.monotonic()-wall, 4),
                  "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        print(json.dumps(result, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()

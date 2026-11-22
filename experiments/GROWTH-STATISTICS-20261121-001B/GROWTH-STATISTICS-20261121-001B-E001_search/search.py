"""One isolated run of each proposal policy and its bounded witness checks."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from random import Random
import signal
from time import perf_counter_ns, process_time_ns

from growth import (GrowthCapacity, HORIZON, collision_read, compact_growth,
                    early_bin, is_whole_closure_relay, late_signature, replay)
from source import Proposal, certify, decode, founder_code, independent_proposal, mutate, partition


SEARCH_CPU_NS = 80_000_000
VERIFY_CPU_NS = 50_000_000
ATTEMPT_LIMIT = 16_384
NAMESPACE = "GROWTH-STATISTICS-20261121-001B/v1"
LAWS = ("parity", "nae")
ARMS = ("independent", "diversity")


def rng_for(*key):
    seed = sha256("/".join(map(str, (NAMESPACE, *key))).encode()).digest()
    return Random(int.from_bytes(seed, "big"))


class CPUExhausted(Exception):
    pass


@dataclass
class Window:
    allowance_ns: int

    def __enter__(self):
        self.previous = signal.signal(signal.SIGPROF, self.interrupt)
        self.cpu = process_time_ns()
        self.wall = perf_counter_ns()
        # The kernel signal is a backstop. Sampled process CPU, checked on
        # both sides of every transaction, is the scoring boundary.
        signal.setitimer(signal.ITIMER_PROF, (self.allowance_ns + 2_000_000) / 1e9)
        return self

    def __exit__(self, *_):
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, self.previous)

    def interrupt(self, *_):
        raise CPUExhausted

    def elapsed(self):
        return process_time_ns() - self.cpu

    def remaining(self):
        return self.elapsed() < self.allowance_ns

    def ledger(self):
        used = self.elapsed()
        return {"allocated_cpu_ns": self.allowance_ns, "actual_cpu_ns": used,
                "wall_ns": perf_counter_ns() - self.wall,
                "unused_cpu_ns": max(0, self.allowance_ns - used),
                "boundary_overshoot_ns": max(0, used - self.allowance_ns)}


def read_trial(proposal, law, region, seen, excluded):
    start = decode(proposal)
    if start is None:
        return {"status": "invalid_extra"}
    code = founder_code(start)
    if code in excluded:
        return {"founder": code, "status": "public_reference"}
    actual_region = partition(code)
    if actual_region != region:
        return {"partition": actual_region, "status": "partition_refusal"}
    result = {"founder": code, "partition": actual_region}
    if code in seen:
        return {**result, "status": "duplicate"}
    seen.add(code)
    stars = start.stars
    certificate = certify(stars)
    result.update({"lawfulness": certificate, "founder_count": len(stars),
                   "physical_distinctions": len(set().union(*map(set, stars)))})
    if certificate["failures"]:
        return {**result, "status": "invalid_projection"}
    growth = compact_growth(stars, law)
    relay = is_whole_closure_relay(growth, law)
    return {**result, "status": growth["stop"], "growth": growth, "known_closure_relay": relay,
            "late_signature": None if relay else late_signature(growth),
            "collision_read": collision_read(growth, len(stars))}


def choose_proposal(index, arm, first, archive, rng):
    if index == 0:
        return first, "common", None, None
    if arm == "independent" or not archive or rng.randrange(4) == 0:
        return independent_proposal(rng), "independent", None, None
    key = rng.choice(tuple(archive))
    parent, parent_index = archive[key]
    child, edit = mutate(parent, rng)
    return child, edit, parent_index, key


def search(law, arm, index, first, region, excluded, search_budget=SEARCH_CPU_NS):
    rng = rng_for(region, law, index, arm)
    rows = []
    archive = {}
    seen = set()
    window = Window(search_budget)
    stopped = "proposal_limit"
    active = None
    try:
        with window:
            for attempt in range(ATTEMPT_LIMIT):
                if not window.remaining():
                    stopped = "cpu_limit"
                    break
                cpu, wall = process_time_ns(), perf_counter_ns()
                active = {"index": attempt, "start_cpu_ns": cpu - window.cpu,
                          "start_wall_ns": wall - window.wall}
                proposal, move, parent, key = choose_proposal(attempt, arm, first, archive, rng)
                active.update({"move": move, "parent_attempt": parent, "parent_bin": key})
                active.update(read_trial(proposal, law, region, seen, excluded))
                if active["status"] != "partition_refusal":
                    active["proposal"] = proposal.record()
                if arm == "diversity" and "growth" in active:
                    slot = early_bin(active["growth"])
                    active["archive_bin"] = slot
                    active["archive_insert"] = slot not in archive
                    archive.setdefault(slot, (proposal, attempt))
                active["charged_cpu_ns"] = process_time_ns() - cpu
                active["charged_wall_ns"] = perf_counter_ns() - wall
                active["eligible"] = window.remaining()
                rows.append(active)
                active = None
                if not rows[-1]["eligible"]:
                    stopped = "cpu_limit_boundary"
                    break
    except CPUExhausted:
        if active is not None and (not rows or rows[-1] is not active):
            active.update({"eligible": False, "status": "interrupted_by_cpu",
                           "charged_cpu_ns": process_time_ns() - window.cpu - active["start_cpu_ns"],
                           "charged_wall_ns": perf_counter_ns() - window.wall - active["start_wall_ns"]})
            rows.append(active)
        stopped = "cpu_signal"
    completed = sum(row["eligible"] for row in rows)
    evaluated = sum(row["eligible"] and "growth" in row for row in rows)
    return {"rows": rows, "stop": stopped, "budget": window.ledger(), "completed_attempts": completed,
            "evaluated_founders": evaluated, "outcomes": Counter(row["status"] for row in rows)}


def rank_pair(pair):
    left, right = pair
    m, n = left["founder_count"], right["founder_count"]
    a, b = left["physical_distinctions"], right["physical_distinctions"]
    return (max(m, n), m + n, max(a, b), a + b, tuple(sorted((left["founder"], right["founder"]))))


def selected_pairs(rows, dictionary):
    novel = defaultdict(list)
    stratum = defaultdict(list)
    for row in rows:
        if not row["eligible"] or "growth" not in row:
            continue
        signature = row["late_signature"]
        if signature is not None and signature not in dictionary:
            novel[signature].append(row)
        collision = row["collision_read"]
        if collision is not None:
            stratum[collision[0]].append(row)

    primary, minima = [], []
    for key, group in novel.items():
        if len(group) < 2:
            continue
        first = tuple(group[:2])
        smallest = sorted(group, key=lambda r: (r["founder_count"], r["physical_distinctions"],
                                                 r["founder"]))[:2]
        least = tuple(sorted(smallest, key=lambda r: r["index"]))
        # All pairs share the signature. For lexicographic rank, a smaller
        # founder count dominates any physical distinction count or code.
        primary.append(("novel", "first", key, first))
        if least != first:
            minima.append(("novel", "minimum", key, least))
    primary.sort(key=lambda item: (item[3][1]["index"], item[2]))
    minima.sort(key=lambda item: (rank_pair(item[3]), item[2]))
    yield from primary
    yield from minima

    # First and minimum are chosen separately across every observed collision
    # with distinct founder identities. Keep the selection itself budgeted.
    first_collision = minimum_collision = None
    for key, group in stratum.items():
        if len({row["collision_read"][2] for row in group}) < 2:
            continue
        for a, b in combinations(group, 2):
            if a["collision_read"][2] == b["collision_read"][2]:
                continue
            pair = (a, b)
            by_order = (b["index"], a["index"])
            by_size = rank_pair(pair)
            if first_collision is None or by_order < first_collision[0]:
                first_collision = (by_order, key, pair)
            if minimum_collision is None or by_size < minimum_collision[0]:
                minimum_collision = (by_size, key, pair)
    if first_collision is not None:
        yield "collision", "first", first_collision[1], first_collision[2]
        if minimum_collision[2] != first_collision[2]:
            yield "collision", "minimum", minimum_collision[1], minimum_collision[2]


def verify_founder(row, law, horizon):
    start = decode(Proposal.from_record(row["proposal"]))
    if start is None or founder_code(start) != row["founder"]:
        raise ValueError("scored founder identity disagrees with proposed source")
    result = replay(start, law, horizon)
    expected = row["growth"]["rounds"][:horizon]
    if result["rounds"] != expected:
        raise ValueError("literal growth disagrees with compact birth and loose counts")
    if (result["status"] == "live") != bool(expected[-1]["live"]):
        raise ValueError("literal growth disagrees with compact openness")
    return result


def verify(rows, law, dictionary, verification_budget=VERIFY_CPU_NS):
    events, active = [], None
    exhausted = False
    window = Window(verification_budget)
    try:
        with window:
            for kind, choice, key, pair in selected_pairs(rows, dictionary):
                if not window.remaining():
                    exhausted = True
                    break
                began, wall = process_time_ns(), perf_counter_ns()
                active = {"kind": kind, "choice": choice, "key": key, "rank": rank_pair(pair),
                          "attempts": [row["index"] for row in pair], "replays": []}
                horizon = HORIZON if kind == "novel" else 3
                try:
                    for row in pair:
                        active["replays"].append(verify_founder(row, law, horizon))
                    active["status"] = "verified"
                except GrowthCapacity as error:
                    active["status"] = str(error)
                except ValueError as error:
                    active["status"] = "replay_disagrees"
                    active["detail"] = str(error)
                active["charged_cpu_ns"] = process_time_ns() - began
                active["charged_wall_ns"] = perf_counter_ns() - wall
                active["end_cpu_ns"] = window.elapsed()
                if not window.remaining():
                    active["status"] = "boundary_unfinished"
                    exhausted = True
                events.append(active)
                active = None
                if exhausted:
                    break
    except CPUExhausted:
        if active is not None and (not events or events[-1] is not active):
            active.update({"status": "interrupted_by_cpu", "end_cpu_ns": window.elapsed()})
            events.append(active)
        exhausted = True
    return {"events": events, "budget": window.ledger(), "verification_exhausted": exhausted}


def pair(law, index, region, dictionary, excluded, budgets=None):
    setup_cpu, setup_wall = process_time_ns(), perf_counter_ns()
    first = independent_proposal(rng_for(region, law, index, "first"))
    order = rng_for(region, law, index, "arm-order").sample(ARMS, 2)
    shared = {"cpu_ns": process_time_ns() - setup_cpu, "wall_ns": perf_counter_ns() - setup_wall}
    search_ns, verify_ns = budgets or (SEARCH_CPU_NS, VERIFY_CPU_NS)
    results = {}
    for arm in order:
        result = search(law, arm, index, first, region, excluded, search_ns)
        result["verification"] = verify(result["rows"], law, dictionary, verify_ns)
        results[arm] = result
    common_completed = min(r["completed_attempts"] for r in results.values())
    for arm in order:
        result = results[arm]
        result["equal_count_verification"] = verify(result["rows"][:common_completed], law, dictionary, verify_ns)
    return {"law": law, "index": index, "partition": region, "execution_order": order,
            "shared_setup": shared, "common_completed_attempts": common_completed, "arms": results}

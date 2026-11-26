"""Replay diagnostic growth and return series from the registered definitions."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path
import signal

import networkx as nx

from prediction_recount import DATA, MODES, REGISTRATION, item_key, read_json, read_lines, series_flags


@dataclass(frozen=True)
class Part:
    members: tuple
    counts: tuple
    maximal_met_sets: tuple
    direct_meetings: frozenset
    past_start: bool

    def form(self):
        return tuple(sorted(self.counts)), tuple(sorted(map(len, self.maximal_met_sets)))

    def meeting_pattern(self):
        index = {member: i for i, member in enumerate(self.members)}
        return frozenset(frozenset(index[u] for u in met) for met in self.maximal_met_sets)


def same_part(left, right):
    if left.form() != right.form():
        return False
    left_pattern = left.meeting_pattern()
    right_pattern = right.meeting_pattern()
    if left.counts == right.counts and left_pattern == right_pattern:
        return True

    def incidence(counts, pattern):
        graph = nx.Graph()
        graph.add_nodes_from((i, {"kind": ("member", *count)}) for i, count in enumerate(counts))
        for index, met in enumerate(pattern, len(counts)):
            graph.add_node(index, kind=("met set", len(met)))
            graph.add_edges_from((index, member) for member in met)
        return graph

    return nx.vf2pp_is_isomorphic(incidence(left.counts, left_pattern),
                                incidence(right.counts, right_pattern), node_label="kind")


def maximal_sets(sets):
    maximal = []
    for candidate in sorted(sets, key=lambda values: (-len(values), tuple(sorted(values)))):
        if not any(candidate <= larger for larger in maximal):
            maximal.append(candidate)
    return tuple(maximal)


class Roster:
    def __init__(self, holders, places, members):
        self.members = members
        met = defaultdict(set)
        self.direct = set()
        for u in members:
            for distinction in places[u]:
                for v in holders[distinction]:
                    if u == v:
                        continue
                    met[v].add(u)
                    if v in members:
                        self.direct.add(tuple(sorted((u, v))))
        self.met = {frozenset(values) for values in met.values() if len(values) > 1}
        self.joinable = nx.Graph()
        self.joinable.add_nodes_from(members)
        self.joinable.add_edges_from(pair for values in self.met for pair in combinations(values, 2))

    def parts(self):
        result = []
        met_by_member = defaultdict(set)
        for values in self.met:
            for member in values:
                met_by_member[member].add(values)
        direct_by_member = defaultdict(set)
        meeting_members = set()
        for u, v in self.direct:
            direct_by_member[u].add((u, v))
            meeting_members.update((u, v))
        for part in sorted(nx.connected_components(self.joinable), key=min):
            members = tuple(sorted(part))
            met = set().union(*(met_by_member[u] for u in members))
            direct = frozenset(pair for u in members for pair in direct_by_member[u] if pair[1] in part)
            result.append(Part(members, tuple(self.members[u] for u in members), maximal_sets(met), direct,
                               part.isdisjoint(meeting_members)))
        return result

    def groups(self):
        pairs = {tuple(sorted(pair)) for pair in self.joinable.edges}
        larger = []
        largest_met = maximal_sets(self.met)
        for clique in nx.find_cliques(self.joinable):
            if len(clique) < 3:
                continue
            values = set(clique)
            if any(values <= met for met in largest_met):
                continue
            larger.append(tuple(sorted(values)))
            pairs.difference_update(combinations(sorted(values), 2))
        return sorted(larger) + sorted(pairs)


def parity_row(distinctions):
    return sum(1 << d for d in distinctions)


def eliminate(row, basis):
    while row:
        head = row.bit_length() - 1
        if head not in basis:
            return row
        row ^= basis[head]
    return 0


class Growth:
    def __init__(self, stars, item):
        self.places = [tuple(star) for star in stars]
        self.parents = [() for _ in stars]
        self.birth_round = [0 for _ in stars]
        self.holders = defaultdict(list)
        for knot, star in enumerate(stars):
            for distinction in star:
                self.holders[distinction].append(knot)
        self.barred = set()
        self.next_name = max(self.holders) + 1
        self.round = 0
        self.take_rule = item["rule"]
        self.treatment = "WAIT" if item["base"].startswith("RING-LAW") else item["base"].split("(")[1][:-1]
        self.floor = item["base"].startswith("COPY-LAW")
        self.fillers = "+FILLERS" in item["base"]
        self.choice = item["choice"]
        self.fresh_by_parents = item["group"] == "fbp"
        self.demand_before_takes = item["group"] == "dbt"
        self.parity = item["knot_law"] == "parity"
        self.basis = {}
        if self.parity:
            self.add_to_span(self.places)

    def add_to_span(self, stars):
        for star in stars:
            remaining = eliminate(parity_row(star), self.basis)
            if remaining:
                self.basis[remaining.bit_length() - 1] = remaining

    def member_inputs(self):
        loose = defaultdict(list)
        barred = Counter()
        for distinction, holders in self.holders.items():
            if len(holders) == 1:
                holder = holders[0]
                if distinction in self.barred:
                    barred[holder] += 1
                else:
                    loose[holder].append(distinction)
        return {knot: sorted(ds) for knot, ds in loose.items()}, barred

    def roster(self):
        loose, barred = self.member_inputs()
        members = {knot: (len(values), barred[knot]) for knot, values in loose.items()}
        return Roster(self.holders, self.places, members)

    def bar(self, members):
        loose, _ = self.member_inputs()
        self.barred.update(d for knot in members for d in loose.get(knot, ()))

    def meets(self, knot):
        return {v for d in self.places[knot] for v in self.holders[d] if v != knot}

    def taking_candidates(self, parents):
        if self.take_rule is None:
            return []
        if len(parents) > 1:
            if self.take_rule not in ("MET", "MET:join"):
                return []
            sources = set.intersection(*(self.meets(p) for p in parents))
        elif self.take_rule == "Q":
            return sorted(d for d in self.places[parents[0]] if len(self.holders[d]) > 1)
        elif self.take_rule in ("MET", "MET:offshoot", "MET:join"):
            sources = self.meets(parents[0]) if self.take_rule != "MET:join" else set()
        else:
            parent = parents[0]
            rule, _, variant = self.take_rule.partition(":")
            if variant == "join" and len(self.parents[parent]) < 2:
                return []
            if variant == "offshoot" and len(self.parents[parent]) != 1:
                return []
            sources = set()
            frontier = {parent}
            for _ in range(int(rule[-1])):
                frontier = {q for p in frontier for q in self.parents[p]}
                if rule.startswith("UP-TO"):
                    sources.update(frontier)
            sources.update(frontier)
        held = {d for parent in parents for d in self.places[parent]}
        return sorted({d for source in sources for d in self.places[source]
                       if len(self.holders[d]) >= 2 and d not in held})

    def choose(self, options, parents, offshoot_index):
        if self.choice == "NEWEST":
            return options[-1]
        if self.choice == "BY-COUNT":
            return options[len(self.places[parents[0]]) % len(options)]
        if self.choice == "IN-TURN" and len(parents) == 1:
            return options[offshoot_index % len(options)]
        return options[0]

    def step(self):
        roster = self.roster()
        loose, barred = self.member_inputs()
        groups = roster.groups()
        owed = Counter(member for group in groups for member in group)
        short = {member for member, ds in loose.items() if owed[member] > len(ds)}
        waiting = short if self.treatment == "WAIT" else set()
        retired = short if self.treatment == "RETIRE" else set()
        births = [group for group in groups if short.isdisjoint(group)]
        joins = Counter(member for birth in births for member in birth)
        for member in sorted(set(loose) - waiting - retired):
            births.extend((member,) for _ in range(len(loose[member]) - joins[member]))
        first = len(self.places)
        spent = Counter()
        offshoots = Counter()
        old_inputs, inputs, take_options, taken = [], [], [], []
        for parents in births:
            ds = [loose[p][spent[p]] for p in parents]
            spent.update(parents)
            options = self.taking_candidates(parents)
            extra = [self.choose(options, parents, offshoots[parents[0]])] if options else []
            if len(parents) == 1:
                offshoots.update(parents)
            old_inputs.append(ds)
            inputs.append(ds + extra)
            take_options.append(len(options))
            taken.append(extra)

        demand_inputs = old_inputs if self.demand_before_takes else inputs
        temporary = self.holders.copy()
        for index, ds in enumerate(demand_inputs, first):
            for d in ds:
                temporary[d] = temporary[d] + [index]
        hypothetical = {u: (len(loose[u]), barred[u]) for u in waiting}
        hypothetical.update({u: (1, 0) for u in range(first, first + len(births))})
        demand_roster = Roster(temporary, self.places + demand_inputs, hypothetical)
        demand = Counter(member for group in demand_roster.groups() for member in group)

        self.round += 1
        self.bar(retired)
        ledger = []
        for i, (parents, ds) in enumerate(zip(births, inputs)):
            name = first + i
            p = len(parents) if self.fresh_by_parents else len(set(ds))
            d = demand[name]
            if self.parity and not eliminate(parity_row(ds), self.basis):
                f = 0
            elif self.floor:
                f = max(3 - p, 1)
            else:
                f = min(3, max(d, 3 - p, 1))
            usable = min(f, d) if self.fillers else f
            ledger.append({"id": name, "kind": "join" if len(parents) > 1 else "offshoot", "parents": list(parents),
                           "inputs": [[d, list(self.holders[d])] for d in ds], "taken_by_rule": taken[i],
                           "D": d, "p": p, "f": f, "usable": usable, "barred": f - usable})
        for birth, ds in zip(ledger, inputs):
            name, f = birth["id"], birth["f"]
            fresh = list(range(self.next_name, self.next_name + f))
            self.next_name += f
            self.barred.update(fresh[birth["usable"]:])
            places = tuple(ds + fresh)
            for distinction in places:
                self.holders[distinction].append(name)
            self.places.append(places)
            self.parents.append(tuple(birth["parents"]))
            self.birth_round.append(self.round)
        if self.parity:
            self.add_to_span(self.places[first:])
        return {"round": self.round, "members_before": sorted(loose),
                "parts_before": [list(part.members) for part in roster.parts()], "short": sorted(short),
                "waiting": sorted(waiting), "retired": sorted(retired), "births": ledger}, take_options


def descent_labels(first_parts, parents, start, final):
    labels = [0] * len(parents)
    for index, part in enumerate(first_parts):
        for member in part.members:
            labels[member] = 1 << index
    for child in range(start, final):
        for parent in parents[child]:
            labels[child] |= labels[parent]
    return labels


def first_returns(parts_by_round, parents, ages, past):
    records = {}
    for s, source in enumerate(parts_by_round[:-1]):
        open_parts = {i for i, part in enumerate(source) if not past or part.past_start}
        if not open_parts:
            continue
        start = next((i for i, age in enumerate(ages) if age > s), len(ages))
        labels = descent_labels(source, parents, start, len(parents))
        for t in range(s + 1, len(parts_by_round)):
            possible = defaultdict(list)
            unions = []
            for q, returned in enumerate(parts_by_round[t]):
                union, common = 0, -1
                for member in returned.members:
                    union |= labels[member]
                    common &= labels[member]
                unions.append((union, common))
                if not common or not any(ages[u] > s for u in returned.members):
                    continue
                while common:
                    bit = common & -common
                    common ^= bit
                    i = bit.bit_length() - 1
                    if i in open_parts and same_part(source[i], returned):
                        possible[i].append(q)
            for i, returns in possible.items():
                returned_set = set(returns)
                bit = 1 << i
                given = [q for q, (union, _) in enumerate(unions) if q not in returned_set and union & bit]
                mixed = sum(not bool(unions[q][1] & bit) for q in given)
                records[(s, i)] = (t, returns, len(given), mixed)
            open_parts.difference_update(possible)
            if not open_parts:
                break
    return records


def return_series(parts_by_round, returns, greatest=False):
    followed = {(t, choices[-1] if greatest else choices[0]) for t, choices, _, _ in returns.values()}
    for origin in sorted(set(returns) - followed):
        s, i = origin
        p0 = parts_by_round[s][i].members
        ticks = []
        periods = []
        while (s, i) in returns:
            t, choices, off, mixed = returns[(s, i)]
            target = choices[-1] if greatest else choices[0]
            after = parts_by_round[t][target]
            carried = {pair for met in after.maximal_met_sets for pair in combinations(sorted(met), 2)}
            ticks.append([t, list(after.members), off, mixed, len(choices) - 1,
                          len(after.direct_meetings), len(after.direct_meetings - carried)])
            periods.append(t - s)
            s, i = t, target
        yield {"t0": origin[0], "P0": list(p0), "size": len(p0), "periods": periods, "ticks": ticks}


def timed_out(*_):
    raise TimeoutError("diagnostic replay exceeded its per-case CPU limit")


def replay_listings(limit, seconds):
    result = {"runs": 0, "matched_runs": 0, "rounds_compared": 0, "births_compared": 0,
              "series_compared": 0, "unmatched": [], "not_run": [], "observed_off2": []}
    for row in read_lines(DATA / "replay_census_listings.jsonl.gz", limit):
        key = item_key(row["item"])
        result["runs"] += 1
        signal.setitimer(signal.ITIMER_PROF, seconds)
        try:
            model = Growth(row["start_places"], row["item"])
            parts = [model.roster().parts()]
            same = True
            for expected in row["rounds"]:
                observed, _ = model.step()
                result["rounds_compared"] += 1
                result["births_compared"] += len(expected["births"])
                problem = [field for field in expected if expected[field] != observed[field]]
                if problem:
                    differing = next(([a, b] for a, b in zip(expected["births"], observed["births"]) if a != b), None)
                    result["unmatched"].append({"item": key, "round": expected["round"], "fields": problem,
                                                "first_changed_birth": differing})
                    same = False
                    break
                parts.append(model.roster().parts())
            if not same:
                continue
            for mode in MODES:
                returns = first_returns(parts, model.parents, model.birth_round, past=mode == "past")
                observed = list(return_series(parts, returns))
                recorded = {(r["t0"], tuple(r["P0"])): r for r in row[f"series_{mode}"]}
                relevant = { (r["t0"], tuple(r["P0"])): r for r in observed if r["size"] > 1 or any(tick[2] for tick in r["ticks"]) }
                # The diagnostic files retain some singleton series when they give parts off.
                result["series_compared"] += len(recorded)
                for origin, saved in recorded.items():
                    if origin not in relevant or any(relevant[origin][field] != saved[field] for field in relevant[origin]):
                        result["unmatched"].append({"item": key, "mode": mode, "recorded_series": saved,
                                                    "observed_series": relevant.get(origin)})
                        same = False
                result["observed_off2"].append({"item": key, "mode": mode,
                    "any": any(series_flags(r)["series_off2"] for r in observed),
                    "multi_member": any(r["size"] > 1 and series_flags(r)["series_off2"] for r in observed)})
            result["matched_runs"] += same
        except TimeoutError:
            result["not_run"].append(key)
        finally:
            signal.setitimer(signal.ITIMER_PROF, 0)
    return result


def grow_with_bar(stars, item, until, barred_round=None, bar=()):
    model = Growth(stars, item)
    parts = []
    for r in range(until + 1):
        parts.append(model.roster().parts())
        if r == until:
            break
        if r == barred_round:
            model.bar(bar)
        model.step()
    returns = first_returns(parts, model.parents, model.birth_round, past=False)
    return parts, returns


def followed_ticks(parts, returns, r, members):
    i, = [i for i, part in enumerate(parts[r]) if part.members == tuple(members)]
    ticks = []
    while (r, i) in returns:
        r, choices, _, _ = returns[(r, i)]
        i = choices[0]
        ticks.append(r)
    return ticks


def two_knot(limit):
    stars = read_json(REGISTRATION / "starts.json")["named"]["two-knot"]
    result = []
    for row in read_json(DATA / "p10.json")["rows"][:limit]:
        original, returns = grow_with_bar(stars, row, 18)
        r3 = [list(part.members) for part in original[3]]
        r4 = [list(part.members) for part in original[4]]
        ones = [part for part in r4 if len(part) == 1]
        four, = [part for part in r4 if len(part) == 4]
        parts, bar_returns = grow_with_bar(stars, row, 18, 4, four)
        actual = {"parts_r3": r3, "parts_r4": r4,
                  "one_member_ticks_A": [followed_ticks(original, returns, 4, m) for m in ones],
                  "one_member_ticks_four_barred": [followed_ticks(parts, bar_returns, 4, m) for m in ones],
                  "three_barred": []}
        for barred, other in (r3, r3[::-1]):
            parts, bar_returns = grow_with_bar(stars, row, 18, 3, barred)
            actual["three_barred"].append({"barred": barred, "other": other,
                                           "other_ticks_A": followed_ticks(original, returns, 3, other),
                                           "other_ticks_barred": followed_ticks(parts, bar_returns, 3, other)})
        result.append({"item": item_key(row), "matches": all(row[key] == value for key, value in actual.items()), **actual})
    return result


def ladder_returns(limit):
    named = read_json(REGISTRATION / "starts.json")["named"]
    selected = [row for row in read_lines(DATA / "run3.jsonl.gz")
                if row["start"] == "D2(4,3)" and row["choice"] == "NEWEST" and row["k"] in (3, 4)]
    result = []
    for row in selected[:limit]:
        model = Growth(named[row["start"]], row)
        initial, = model.roster().parts()
        original = set(initial.members)
        first_take = None
        rounds_returning = []
        for t in range(1, row["rounds"] + 1):
            ledger, _ = model.step()
            if first_take is None and any(b["kind"] == "offshoot" and b["parents"][0] in original and b["taken_by_rule"]
                                          for b in ledger["births"]):
                first_take = t
            returning = [part for part in model.roster().parts() if same_part(initial, part)]
            if returning:
                rounds_returning.append(t)
                original.update(member for part in returning for member in part.members)
        result.append({"item": item_key(row), "k": row["k"], "rounds_grown": row["rounds"],
                       "returns": rounds_returning, "first_ring_offshoot_take": first_take,
                       "matches": rounds_returning == row["start_roster_returns"] and first_take == row["ring_member_offshoot_first_take"]})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--section", choices=("replay", "P7late", "P10"), required=True)
    parser.add_argument("--limit", type=int, help="Take a prefix for timing.")
    parser.add_argument("--case-cpu-seconds", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    signal.signal(signal.SIGPROF, timed_out)
    if args.section == "replay":
        data = replay_listings(args.limit, args.case_cpu_seconds)
    elif args.section == "P7late":
        data = ladder_returns(args.limit)
    else:
        data = two_knot(args.limit)
    report = json.dumps({"section": args.section, "prefix": args.limit, "result": data}, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(report, end="")
    else:
        args.output.write_text(report)


if __name__ == "__main__":
    main()

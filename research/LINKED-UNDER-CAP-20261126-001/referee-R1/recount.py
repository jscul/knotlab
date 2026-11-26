"""Recount the archives with one vote per archive entry or per placed change."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice, permutations, product
import json
from pathlib import Path
from time import perf_counter

from networkx.generators.atlas import graph_atlas_g
from networkx import is_connected

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SENDERS = ("g1:3@0", "g3:22@0", "g6:122@0", "g7:122@0", "stub")


def records(filename, limit):
    with gzip.open(STUDY / filename, "rt") as stream:
        return [json.loads(line) for line in islice(stream, limit)]


def key(r):
    return r["law"], r["A"], r["B"]


def group(r):
    return r["law"] + (" switch" if r["A"].startswith("tri:") else " receivers")


def sited_entries():
    names = ["ring", "copier", "source"]
    for index, g in enumerate(graph_atlas_g()):
        n = len(g)
        if not 1 <= n <= 4 or not is_connected(g):
            continue
        nodes = tuple(range(n))
        sym = [p for p in permutations(nodes)
               if all(g.has_edge(p[u], p[v]) for u, v in g.edges)]
        for loose in product(range(4), repeat=n):
            if not any(loose) or any(g.degree(u) + loose[u] < 3 for u in nodes):
                continue
            orbit = [tuple(loose[i] for i in p) for p in sym]
            if loose != min(orbit):
                continue
            fixed = [p for p, other in zip(sym, orbit) if loose == other]
            for site in nodes:
                if site == min(p[site] for p in fixed):
                    names.append(f"n{n}:g{index}:" + "".join(map(str, loose)) + f"@{site}")
    return names


def metric(counter, change):
    t, s, end = (change[k] for k in ("t0", "sharings", "rounds"))
    target = t+s+1 if s is not None else None
    heard = change["heard"]
    counter["placed"] += 1
    counter["heard"] += heard is not None
    counter["reached_benchmark"] += target is not None and target <= end
    counter["at_benchmark"] += heard is not None and heard == target
    counter["heard_before_benchmark"] += heard is not None and target is not None and heard < target
    counter["heard_after_benchmark"] += heard is not None and target is not None and heard > target
    counter["heard_and_benchmark_reached"] += heard is not None and target is not None and target <= end
    counter["benchmark_within_32"] += target is not None and target <= 32
    counter["no_sharing_count"] += s is None


def again(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[group(r)].append(r)
        groups["all"].append(r)
    out = {}
    for name, rs in groups.items():
        tests = {}
        for t in (3, 7, 11, 15):
            totals, endpoints, hearings, sharings, crossed = Counter(), Counter(), Counter(), Counter(), Counter()
            for r in rs:
                c = next((c for c in r["changes"] if c["t0"] == t), None)
                if c is None:
                    totals["schedule_ended_earlier"] += 1
                elif c.get("none linked"):
                    totals["no_linked_target"] += 1
                else:
                    metric(totals, c)
                    endpoints[c["rounds"]] += 1
                    sharings[c["sharings"]] += 1
                    if c["heard"] is not None:
                        hearings[c["heard"]] += 1
                    if t > 3:
                        h1 = r["changes"][0]["heard"]
                        crossed["first_heard_somewhere"] += h1 is not None
                        crossed["first_heard_by_setting"] += h1 is not None and h1 <= t
                        crossed["first_heard_and_second_benchmark_reached"] += (
                            h1 is not None and t+c["sharings"]+1 <= c["rounds"])
            tests[t] = dict(counts=totals, hearings_by_round=hearings, sharings=sharings,
                            common_endpoints=endpoints, with_first_hearing=crossed)
        ends = Counter()
        relink = 0
        for r in rs:
            post = r["changes"][0]["linked after it"]
            pos = next((i for i, v in enumerate(post) if i >= 3 and v is not True), None)
            if pos is None:
                ends["still linked"] += 1
            else:
                ends[f'{pos+1} {"apart" if post[pos] is False else "missing end"}'] += 1
                relink += any(v is True for v in post[pos+1:])
        out[name] = dict(pairs=len(rs), setting=tests, first_link_loss=ends, relinked=relink,
                         first_hearers_by_receiver=Counter(r["A"] for r in rs if r["changes"][0]["heard"] is not None))
    return out


def measures(rs):
    totals, by_t, positive, hearing_rounds = defaultdict(Counter), defaultdict(Counter), Counter(), Counter()
    endpoints = Counter()
    links_at = {}
    for t in (3, 4, 8, 9, 16, 17):
        values = [r["linked"][t-1] for r in rs if r["rounds"] >= t]
        links_at[t] = {"read":len(values), "true":values.count(True),
                       "apart":values.count(False), "end_absent":values.count(None)}
    for r in rs:
        assert len(r["linked"]) == r["rounds"]
        endpoints[r["rounds"]] += 1
        for c in r["changes"]:
            t = c["t0"]
            linked = c["linked"]
            assert not linked or r["linked"][t-1] is True
            assert t < c["rounds"] <= r["rounds"]
            three = r["linked"][t+2] if len(r["linked"]) >= t+3 else "unread"
            placement = "linked" if linked else "unlinked"
            categories = [placement]
            if linked and three is True:
                categories.append("linked_pair_three_rounds_later")
                metric(by_t[str(t)], c)
            if not linked:
                categories.append("unlinked_in_linked_pair" if r["linked"][t-1] else "unlinked_in_separate_pair")
            for category in categories:
                metric(totals[category], c)
            if c["heard"] is not None:
                positive[r["A"]] += 1
                hearing_rounds[f'{t}/{c["sharings"]}/{c["heard"]}'] += 1
    stopped_short = Counter(str(r["linked"][-1]) for r in rs if r["rounds"] < 16)
    return dict(pairs=len(rs), links_after_completed_round=links_at, common_baseline_endpoints=endpoints,
                last_link_value_for_baselines_ending_before_16=stopped_short,
                changes=totals, linked_pair_three_rounds_later_by_setting=by_t,
                positive_by_receiver=positive, positive_by_setting_sharings_hearing=hearing_rounds)


def normalize_label(label):
    extra = {"copier": "n2:g3:22@0", "tri:122@0": "n3:g7:122@0"}
    extra.update(dict(zip(SENDERS[:4], ("n1:g1:3@0", "n2:g3:22@0", "n3:g6:122@0", "n3:g7:122@0"))))
    return extra.get(label, label)


def aliases(census, repeat):
    def canonical(r):
        return r["law"], normalize_label(r["A"]), normalize_label(r["B"])
    equivalent = defaultdict(list)
    distinct_unlinked = set()
    for r in census:
        pair = canonical(r)
        equivalent[pair].append(r)
        distinct_unlinked.update((pair, c["t0"], c["knot"]) for c in r["changes"] if not c["linked"])
    for match in equivalent.values():
        if len(match) > 1:
            n = min(r["rounds"] for r in match)
            assert len({tuple(r["linked"][:n]) for r in match}) == 1
    second_keys = [canonical(r) for r in repeat]
    for match in {k for k in second_keys if second_keys.count(k)>1}:
        changes = [r["changes"] for r in repeat if canonical(r)==match]
        assert all(cs == changes[0] for cs in changes)
    return dict(distinct_pair_and_law_preparations=len(equivalent),
                distinct_selected_preparations=len(set(second_keys)),
                distinct_unlinked_placements=len(distinct_unlinked),
                repeated_pair_preparations={"/".join(k):[list(key(r)) for r in rs]
                                            for k,rs in equivalent.items() if len(rs)>1})


def main(limit):
    stamp = perf_counter()
    repeat = []
    for file in ("again_linked_runs_caps36.jsonl.gz", "again_linked_runs_receivers.jsonl.gz"):
        repeat.extend(records(file, limit))
    second = again(repeat)
    census = records("linked_runs.jsonl.gz", limit)
    by_group = defaultdict(list)
    for r in census:
        by_group[group(r)].append(r)
    tabs = {g: measures(rs) for g, rs in by_group.items()}
    tabs["all"] = measures(census)
    expected_names = sited_entries()
    expected_keys = {(f"CAP-{k}", f"tri:{k-2}22@0", far) for k in range(3, 8) for far in expected_names}
    expected_keys.update(("CAP-3", recv, far) for recv in expected_names for far in SENDERS)
    keys = [key(r) for r in census]
    selected = [r for r in census if r["rounds"] >= 16 and r["linked"][15] is True]
    sel_keys = {key(r) for r in selected}
    again_keys = {key(r) for r in repeat}
    ends = {k: sorted(r["B"] for r in selected if group(r) == f"CAP-{k} switch") for k in range(3, 7)}
    integrity = dict(expected_labelled_pairs=len(expected_keys), observed=len(keys), missing=len(expected_keys-set(keys)),
                     extra=len(set(keys)-expected_keys), duplicate_keys=len(keys)-len(set(keys)),
                     groups_in_first_1938=Counter(group(r) for r in census[:1938]),
                     overlap_of_resume_keys=len(set(keys[:1938]) & set(keys[1938:])),
                     second_pass_missing=len(sel_keys-again_keys), second_pass_extra=len(again_keys-sel_keys),
                     second_pass_duplicate_keys=len(repeat)-len(again_keys),
                     selected_without_continuous_link=sum(not all(r["linked"][:16]) for r in selected),
                     selected_by_sender=Counter(r["B"] for r in selected if group(r).endswith("receivers")),
                     same_far_labels_all_four=len(set.intersection(*map(set, ends.values()))), far_labels=ends)
    if limit is None:
        assert not any(integrity[x] for x in ("missing", "extra", "duplicate_keys", "second_pass_missing",
                                              "second_pass_extra", "second_pass_duplicate_keys"))
    first_overlap = Counter()
    for r in repeat:
        c = r["changes"][0]
        if c["heard"] is not None:
            first_overlap[str(c["linked after it"][5])] += 1
    output = dict(weighting="One entry per labelled pair, or one vote per actual placement as indicated.",
                  timing="Benchmark is setting round + sharings + 1, counted against the common endpoint.",
                  three_round_reading="Is any strictly far-owned member still in any receiver class in the unmodified pair?",
                  again=second, census=tabs, coverage=integrity, aliases=aliases(census,repeat),
                  first_hearings_link_status_in_changed_run_at_round_6=first_overlap)
    if limit is None:
        (HERE / "recount.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"{len(repeat)} repeat rows and {len(census)} census rows in {perf_counter()-stamp:.3f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="first 16 rows per file, same reading")
    main(16 if parser.parse_args().pilot else None)

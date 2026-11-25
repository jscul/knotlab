"""Reconcile first meetings and actual two-step takes on the registered matched panel."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json


FAMILY = Path(__file__).resolve().parent.parent
ROOT = FAMILY.parents[2]
ART = ROOT / "artifacts" / FAMILY.parent.name / FAMILY.name
PRODUCER = ART / "producer"
ARCHIVE = ROOT / "research/WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further"


def rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def digest(data):
    return sha256(json.dumps(data, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def event_id(event):
    x, y = sorted((tuple(event["X"]), tuple(event["Y"])))
    return event["s"], x, y


def unique(values):
    return next(iter(values)) if len(values) == 1 else None


class History:
    """Read the support snapshots without invoking a growth or selector implementation."""

    def __init__(self, path):
        self.frames = list(rows(path))
        self.parents, self.made, self.ancestors, self.places = [], [], [], []
        self.prefixes = []
        self.actual = []
        self.decisions = []
        self.born_with = {}
        self.split_classes = {}
        prior_takes = set()
        owners = defaultdict(set)
        prev_hash = ""
        for frame in self.frames:
            t = frame["round"]
            if t:
                self.read_choices(frame, owners, prior_takes)
            prior_takes = {d for b in frame["births"] for d in b["takes"]}
            before = len(self.places)
            by_id = {b["id"]: b for b in frame["births"]}
            for u, places in enumerate(frame["supports"], before):
                ps = by_id[u]["parents"] if t else []
                anc = 0
                for p in ps:
                    anc |= self.ancestors[p] | (1 << p)
                self.parents.append(ps)
                self.made.append(t)
                self.ancestors.append(anc)
                self.places.append(tuple(places))
                for d in places:
                    owners[d].add(u)
            # Only incidences, ancestry, actual choices and bars identify a shared split.
            names = [(b["id"], b["parents"], b["loose"], b["takes"]) for b in frame["births"]]
            prev_hash = digest([prev_hash, frame["supports"], names, frame["barred"]])
            self.prefixes.append(prev_hash)
            barred = set(frame["barred"])
            live = {next(iter(us)) for d, us in owners.items() if len(us) == 1 and d not in barred}
            # A part's members are connected by common witnesses. Historical independent
            # part classes also join any parts whose live members share directly.
            leader = {u: u for u in live}
            def root(u):
                while u != leader[u]:
                    leader[u] = leader[leader[u]]
                    u = leader[u]
                return u
            def union(members):
                members = iter(members)
                first = next(members, None)
                if first is not None:
                    for v in members:
                        leader[root(v)] = root(first)
            for w, ws in enumerate(self.places):
                meeting = set()
                for d in ws:
                    meeting.update(owners[d] & live)
                meeting.discard(w)
                union(meeting)
            for us in owners.values():
                union(us & live)
            self.split_classes[t] = {u: root(u) for u in live}

    def read_choices(self, frame, owners, prior_takes):
        t = frame["round"]
        @lru_cache(None)
        def near(p):
            return set().union(*(owners[d] for d in self.places[p])) - {p}
        @lru_cache(None)
        def far(p):
            direct = near(p)
            return direct.union(*(near(q) for q in direct)) - {p}
        @lru_cache(None)
        def offer(ps):
            held = set().union(*(self.places[p] for p in ps))
            def candidates(reach):
                common = set.intersection(*(reach(p) for p in ps)) - set(ps)
                return {d for w in common for d in self.places[w] if d not in held and len(owners[d]) >= 2}
            return candidates(near), candidates(far)
        for b in frame["births"]:
            ps = tuple(b["parents"])
            c1, c2 = offer(ps)
            sole = unique(c2)
            scores = {d:len(owners[d]) for d in c2}
            best = max(scores.values(), default=0)
            top = {d for d in c2 if scores[d] == best}
            selected = {"MOST": unique(top), "SOLE": sole,
                        "RECENT": sole if sole is not None else unique(c2 & prior_takes),
                        "OUTER": sole if sole is not None else unique(c2 - c1)}
            actual = unique(b["takes"])
            assert len(b["takes"]) <= 1
            self.decisions.append((actual, selected))
            if actual is None:
                continue
            record = [t, b["id"], actual, sorted(c1), sorted(c2)]
            self.actual.append(record)
            offering = min(h for h in owners[actual] if h not in ps and all(h in far(p) for p in ps))
            paths = [[p,offering] if offering in near(p) else
                     [p,min(v for v in near(p) if offering in near(v)),offering] for p in ps]
            self.born_with[b["id"]] = {
                "one_common_offering_holder":offering, "holder_paths_from_parents":paths,
                "round": t, "recipient":b["id"], "parents": list(ps), "c":actual,
                "near_eligible": actual in c1, "C1": sorted(c1), "C2": sorted(c2),
                "holders_before": sorted(owners[actual]), "highest_holder_count":best,
                "most_candidates": sorted(top), "recent_candidates":sorted(c2 & prior_takes),
                "lower_than_the_maximum":scores[actual] < best,
            }

    def ancestry_chain(self, start, end):
        if end == start:
            return [start]
        for p in self.parents[end]:
            if p == start or self.ancestors[p] & (1 << start):
                return self.ancestry_chain(start, p) + [end]
        return []


def normalized_route(r, hist):
    w, u, v = r["w"], r["u"], r["v"]
    ancestry = (r["w_ancestor_u"], r["w_ancestor_v"]) if hist is None else (
        bool(hist.ancestors[u] & (1 << w)), bool(hist.ancestors[v] & (1 << w)))
    return (r["route"],r["w"],r["u"],r["v"],tuple(r["x_arms"]),tuple(r["y_arms"]),
            tuple(r["contacts"]),r.get("near_eligible"),*ancestry)


def event_receipt(e, referee, hist=None):
    if referee:
        linkers = e["linking_knots"]
        made, start_held = e["only_made_knots"], bool(e["start_held_linking_distinctions"])
    else:
        linkers = [w["knot"] for w in e["linking_knots"]]
        made, start_held = e["strict"], e["start_knot_holds_linking_distinction"]
    # The original reader names the roster phase "group" and its demand
    # phase "demand group"; the independent reader names them met and demand.
    names={"group":"met", "demand group":"demand", "met":"met", "demand":"demand", "take":"take"}
    return (*event_id(e),e["t"],sorted(names[x] for x in e["meeting_types"]),sorted(linkers),
            made,start_held,sorted(normalized_route(r,hist) for r in e["routes"]))


def link_signature(e):
    return (e["link_verdict"],e["start_knot_holds_linking_distinction"],
            any(x["class"] == "ancestral common knot" and x["made"] for x in e["linking_knots"]) and e["strict"],
            tuple(sorted({x["class"] for x in e["linking_knots"]})))


def archive_signature(link):
    return (link["verdict"],link["start knot holds a linking distinction"],link["ancestral"],
            tuple(link["classes of linking knots"]))


def archive_checks(case, events, hist, archive, original, statistics):
    archived = archive[case["source"]][case["line"]-1]
    spec = archived["spec"]
    assert [spec[k] for k in ("start","ration","treatment","take","knot_law")] == [
        case["start"],case["ration"],case["treatment"],"MET2-MANY","nae"]
    assert len(archived["rows"]) == case["archive_rows"]
    lookup = {event_id(e):e for e in events}
    by_x = defaultdict(dict)
    for (s,x,y),e in lookup.items():
        by_x[s,x][y] = e
        by_x[s,y][x] = e
    named = original.get((spec["start"],spec["ration"],spec["treatment"]),[])
    for test in named:
        for j in (1,2):
            key = (test["s"],*sorted((tuple(test["X"]),tuple(test["Y"+str(j)]))))
            statistics["named_part_pairs_checked"] += 1
            if key not in lookup or lookup[key]["t"] != test["meets"][j-1]:
                raise AssertionError(("archived named meeting did not replay",case["id"],key))
        statistics["named_four_run_tests_with_both_first_rounds_verified"] += 1
    # Many archive summaries omit part identities. Require a single matching X for
    # each row, distinct compatible Ys, and a distinct X per row at each split.
    matching = {}
    options = []
    for old in archived["rows"]:
        s = old["s"]
        groups = []
        for (level,x),ns in by_x.items():
            if level!=s or len(x)!=old["sizes"][0]:
                continue
            sides=[]
            for j,link in enumerate(old["links"]):
                sides.append([y for y,e in ns.items() if len(y)==old["sizes"][j+1]
                              and e["t"]==old["meets"][j] and link_signature(e)==archive_signature(link)])
            classes = hist.split_classes[s]
            if any(classes[a[0]]!=classes[b[0]] for a in sides[0] for b in sides[1]):
                groups.append((s,x))
        options.append(groups)
    def assign(i,seen):
        for x in options[i]:
            if x in seen:
                continue
            seen.add(x)
            if x not in matching or assign(matching[x],seen):
                matching[x]=i
                return True
        return False
    if not all(assign(i,set()) for i in range(len(options))):
        raise AssertionError(("anonymized archive rows failed one-to-one X matching",case["id"]))
    statistics["anonymized_archive_rows_with_distinct_compatible_first_parts"] += len(options)
    statistics["first_meeting_entries_in_anonymized_rows"] += 2*len(options)


def one_case(case, rule, kl, prod, hist, events, examples):
    key = (case["id"],rule,kl)
    totals = Counter(trajectories=1, eligible_separated_pairs=sum(s.get("eligible_pairs",0)
                     for s in prod["split_coverage"]), births=len(hist.decisions))
    for actual,expected in hist.decisions:
        assert expected[rule] == actual, ("selector mismatch",key,actual,expected)
        totals["action_differs_from_MOST"] += actual!=expected["MOST"]
        totals["took_when_MOST_differs"] += actual is not None and actual!=expected["MOST"]
    totals.update(takes=len(hist.actual), outer_takes=sum(not x["near_eligible"] for x in hist.born_with.values()),
                  lower_than_maximum_takes=sum(x["lower_than_the_maximum"] for x in hist.born_with.values()))
    assert (totals["takes"],totals["outer_takes"]) == (prod["take_count"],prod["outer_take_count"])
    flags = defaultdict(set)
    times = {}
    ancestry = defaultdict(Counter)
    two = defaultdict(lambda:defaultdict(set))
    def example(name, e, r, extra=None):
        k = rule+"/"+kl+"/"+name
        if k not in examples:
            examples[k]={"case":case["id"],"start":case["start"],"ration":case["ration"],
                "treatment":case["treatment"],"s":e["s"],"t":e["t"],"X":e["X"],"Y":e["Y"],
                "phase":r["route"],"u":r["u"],"v":r["v"],"w":r["w"],
                "u_round":hist.made[r["u"]],"v_round":hist.made[r["v"]],"w_round":hist.made[r["w"]],
                "u_parents":hist.parents[r["u"]],"v_parents":hist.parents[r["v"]],
                "arm_from_X":r["x_arms"],"arm_from_Y":r["y_arms"],"same_identity":r["contacts"],
                "all_linking_knots_made":e["strict"],"has_start_held_link":e["start_knot_holds_linking_distinction"],
                **(extra or {})}
    for e in events:
        ek = event_id(e)
        assert ek not in times and e["s"]<e["t"]<=prod["rounds_read"]
        times[ek]=e["t"]
        made=e["strict"]
        wholly=made and not e["start_knot_holds_linking_distinction"]
        directly=False
        common_neither=False
        current_arm_outer=False
        older_arm_outer=False
        common_identity_outer=False
        label={w["knot"]:w["class"] for w in e["linking_knots"]}
        for r in e["routes"]:
            w,u,v=r["w"],r["u"],r["v"]
            if r["route"]=="take":
                tinfo=hist.born_with[r["recipient"]]
                assert r["pre_holder"] in tinfo["holders_before"] and r["contacts"]==[tinfo["c"]]
                assert tinfo["near_eligible"]==r["near_eligible"] and tinfo["round"]==e["t"]
                if not r["near_eligible"]:
                    directly=True
                    example("direct_outer_take",e,r,{"selected":tinfo})
                    if made:
                        example("direct_outer_take_made_linkers",e,r,{"selected":tinfo})
                    if tinfo["lower_than_the_maximum"]:
                        totals["direct_outer_lower_than_maximum_route_occurrences"]+=1
                continue
            assert w!=u and w!=v
            for side,arms in ((u,r["x_arms"]),(v,r["y_arms"])):
                for receiving in (side,w):
                    info=hist.born_with.get(receiving)
                    if info is None or info["near_eligible"] or info["c"] not in arms:
                        continue
                    if info["round"]==e["t"]:
                        current_arm_outer=True
                        common_identity_outer |= info["c"] in r["contacts"]
                        if wholly:
                            example("no_start_held_direct_outer_common_arm",e,r,{"selected":info})
                    elif info["round"]<e["t"]:
                        older_arm_outer=True
            if not hist.made[w]:
                continue
            x=bool(hist.ancestors[u] & (1<<w))
            y=bool(hist.ancestors[v] & (1<<w))
            desc="both" if x and y else "one" if x or y else "neither"
            ancestry["made_common_witness_routes"][desc]+=1
            if made:
                ancestry["all_linking_knots_made"][desc]+=1
            if label[w]=="made, no ancestor of both":
                ancestry["old_negative_ancestry_label"][desc]+=1
                if wholly:
                    ancestry["old_negative_ancestry_label_no_start_holder"][desc]+=1
            if wholly:
                ancestry["no_start_held_link"][desc]+=1
                totals["no_start_held_pure_common_witness_occurrences"]+=1
                totals["no_start_held_pure_common_witness_same_distinction"]+=bool(r["contacts"])
            if not x and not y:
                common_neither=True
            if x!=y and label[w]=="made, no ancestor of both":
                tag="one_sided_ancestry_despite_old_label"
                example(tag,e,r,{"chain_to_u":hist.ancestry_chain(w,u),"chain_to_v":hist.ancestry_chain(w,v)})
                if wholly:
                    example(tag+"_no_start_holder",e,r,{"chain_to_u":hist.ancestry_chain(w,u),
                                                         "chain_to_v":hist.ancestry_chain(w,v)})
            if wholly:
                example("no_start_held_meeting",e,r)
        facts={"meetings":True,"all_linking_knots_made":made,"no_start_held_link":wholly,
               "direct_outer_take":directly,"all_made_direct_outer":made and directly,
               "no_start_held_direct_outer":wholly and directly,
               "outer_take_on_common_witness_arm_in_meeting_round":current_arm_outer,
               "outer_take_on_common_identity_in_meeting_round":common_identity_outer,
               "outer_take_used_on_common_witness_arm_in_earlier_round":older_arm_outer,
               "outer_take_participating_in_meeting_round":directly or current_arm_outer,
               "no_start_held_with_meeting_round_outer_on_common_arm":wholly and current_arm_outer,
               "no_start_held_with_earlier_outer_on_common_arm":wholly and older_arm_outer,
               "all_made_with_meeting_round_outer_on_common_arm":made and current_arm_outer,
               "no_start_held_with_participating_outer_take":wholly and (directly or current_arm_outer),"has_pure_route":bool(e["routes"]),
               "all_made_with_nonancestor_common_witness":made and common_neither,
               "no_start_held_with_nonancestor_common_witness":wholly and common_neither}
        for f,ok in facts.items():
            if ok:
                flags[f].add(ek)
                if f in ("all_linking_knots_made","no_start_held_link"):
                    s,x,y=ek
                    two[f][s,x].add(y)
                    two[f][s,y].add(x)
        if wholly and any(z[0] <= e["t"] and z[2] not in z[3] for z in hist.actual):
            totals["no_start_held_with_outer_by_meeting"]+=1
    for f,ks in flags.items():
        totals[f]=len(ks)
    for f,fs in two.items():
        for (s,x),ys in fs.items():
            if len({hist.split_classes[s][y[0]] for y in ys})>=2:
                totals[f+"_X_with_two_separately_descended_Ys"]+=1
    assert totals["meetings"]==prod["meeting_counts"].get("meetings",0)
    assert totals["no_start_held_link"]==prod["meeting_counts"].get("meetings_through_made_only",0)
    assert totals["direct_outer_take"]==prod["meeting_counts"].get("meetings_with_outer_take_route",0)
    return totals,flags,times,ancestry


def archive_sources(cases):
    archive={name:list(rows(ARCHIVE/name)) for name in {c["source"] for c in cases}}
    original={}
    for name in ("rings.jsonl.gz","census_wide.jsonl.gz","census_near.jsonl.gz","census_five_m2many.jsonl.gz"):
        for item in rows(ARCHIVE/name):
            spec=item["spec"]
            if spec["take"]=="MET2-MANY" and spec["knot_law"]=="nae" and item.get("tests"):
                key=(spec["start"],spec["ration"],spec["treatment"])
                if key in original:
                    assert original[key]==item["tests"]
                original[key]=item["tests"]
    return archive,original


def matched(ordinary,alt,table,kl,rule,cohort):
    for feature in ("takes","outer_takes","meetings","all_linking_knots_made","no_start_held_link",
                    "direct_outer_take","all_made_direct_outer","no_start_held_direct_outer",
                    "all_linking_knots_made_X_with_two_separately_descended_Ys",
                    "no_start_held_link_X_with_two_separately_descended_Ys"):
        baseline=bool(ordinary[0][feature])
        alternative=bool(alt[0][feature])
        counts=table[kl+"/"+rule+"/"+cohort][feature]
        counts["both" if baseline and alternative else "only_MOST" if baseline else
               "only_alternative" if alternative else "neither"]+=1
    if cohort!="all":
        return
    for f in ("meetings","all_linking_knots_made","no_start_held_link","direct_outer_take"):
        counts=table[kl+"/"+rule+"/physical_split_pairs"][f]
        for key in alt[1].get(f,set()):
            s=key[0]
            if ordinary[3][s]!=alt[3][s]:
                counts["different_recorded_state_at_split"]+=1
            elif key not in ordinary[1].get(f,set()):
                counts["same_recorded_split_no_matching_MOST_outcome"]+=1
            else:
                counts["same_split_pair_and_level"]+=1
                if ordinary[2][key]==alt[2][key]:
                    t=alt[2][key]
                    counts["also_same_first_round"]+=1
                    counts["also_same_history_through_first_round"]+=ordinary[3][t]==alt[3][t]


def reconcile_referee(where,key_receipts):
    if not (where/"summary.json").is_file():
        return {"state":"pending","path":str(where.relative_to(ROOT)) if where.is_relative_to(ROOT) else str(where)}
    checks=Counter()
    diffs=Counter()
    first={}
    def verify(k,field,left,right):
        checks[field]+=1
        if left!=right:
            diffs[field]+=1
            first.setdefault(field,{"configuration":k,"producer":left,"referee":right})
    ref_takes=defaultdict(list)
    ref_events=defaultdict(list)
    def key(r):return (r["case"],r["rule"],r["kl"])
    for r in rows(where/"takes.jsonl.gz"):
        ref_takes[key(r)].append([r["t"],r["recipient"],r["c"],r["c1"],r["c2"]])
    for e in rows(where/"first_meetings.jsonl.gz"):
        ref_events[key(e)].append(event_receipt(e,True))
    seen=set()
    for r in rows(where/"cases.jsonl"):
        k=key(r)
        if k not in key_receipts:
            continue
        assert k not in seen
        seen.add(k)
        own=key_receipts[k]
        verify(k,"extent_and_knots",own["extent"],[r["rounds_read"],r["knots"]])
        verify(k,"actual_takes_and_candidates",own["takes"],digest(sorted(ref_takes[k])))
        ev=sorted(ref_events[k])
        verify(k,"first_meeting_id_round_and_kinds",own["parts"],digest([e[:5] for e in ev]))
        verify(k,"linking_knots_start_origin_pure_routes_and_witness_ancestry",own["incidence"],digest(ev))
    return {"state":"agreed" if not diffs and seen==set(key_receipts) else "differences",
            "checks":checks,"differences":diffs,"first_differences":first,
            "missing_cases":sorted(set(key_receipts)-seen),"source":str(where.relative_to(ROOT)) if where.is_relative_to(ROOT) else str(where)}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--referee",type=Path,default=ART/"referee")
    parser.add_argument("--first",type=int)
    parser.add_argument("--output",type=Path,default=ART/"analysis/reach_comparison.json")
    args=parser.parse_args()
    contract=json.loads((FAMILY/"contract.json").read_text())
    cases=json.loads((FAMILY/contract["cases"]).read_text())
    allcases=cases[:args.first]
    laws,ruleset=contract["knot_laws"],contract["rules"]
    inputs={}
    for row in rows(PRODUCER/"results.jsonl"):
        assert row["status"]=="ok"
        x=row["result"]
        k=(x["case"],x["rule"],x["kl"])
        assert k not in inputs
        inputs[k]=x
    assert len(inputs)==len(cases)*len(laws)*len(ruleset)
    archive,original=archive_sources(allcases)
    archive_counts=Counter()
    totals=defaultdict(Counter)
    carrying=defaultdict(Counter)
    matched_table=defaultdict(lambda:defaultdict(Counter))
    ancestry=defaultdict(lambda:defaultdict(Counter))
    stops=defaultdict(Counter)
    examples={}
    receipts={}
    structural_equality=defaultdict(Counter)
    for case in allcases:
        seen={}
        raw_seen={}
        for rule in ruleset:
            for kl in laws:
                k=(case["id"],rule,kl)
                row=inputs[k]
                assert (case["start"],case["ration"],case["treatment"])==(row["start"],row["ration"],row["treatment"])
                hp=row["support_sha256"]
                if hp not in raw_seen:
                    raw_seen[hp]=History(PRODUCER/row["support_file"])
                hist=raw_seen[hp]
                events=list(rows(PRODUCER/row["events_file"]))
                counts,flags,times,an=one_case(case,rule,kl,row,hist,events,examples)
                seen[rule,kl]=counts,flags,times,hist.prefixes
                high=kl+"/"+rule
                for name in ("all",case["source"]):
                    label=high+"/"+name
                    totals[label].update(counts)
                    carrying[label].update(q for q,v in counts.items() if v)
                for group,value in an.items():
                    ancestry[high][group].update(value)
                stops[high][row["stop"]+"/"+str(row["rounds_read"])]+=1
                ev=sorted(event_receipt(e,False,hist) for e in events)
                receipts[k]={"extent":[row["rounds_read"],row["knots"]],"takes":digest(sorted(hist.actual)),
                             "parts":digest([e[:5] for e in ev]),"incidence":digest(ev)}
                if rule=="MOST" and kl=="nae":
                    archive_checks(case,events,hist,archive,original,archive_counts)
        for rule in ruleset:
            eq=structural_equality[rule]
            eq["source_configurations"]+=1
            eq["same_support_history_under_both_knot_laws"]+=seen[rule,"nae"][3]==seen[rule,"parity"][3]
            a=receipts[case["id"],rule,"nae"]
            b=receipts[case["id"],rule,"parity"]
            eq["same_first_meetings_and_routes"]+=a["incidence"]==b["incidence"]
            if rule!="MOST":
                for kl in laws:
                    for cohort in ("all",case["source"]):
                        matched(seen["MOST",kl],seen[rule,kl],matched_table,kl,rule,cohort)
    result={"source_settings":len(allcases),"executions":len(receipts),"source_settings_per_knot_law_and_rule":len(allcases),
            "weighting":"Each archived case appears once per selector and knot law. Repeated event, witness and route occurrences may share physical knots. Conditional archive cohort.",
            "counts":totals,"source_settings_carrying_each_outcome":carrying,
            "stop_and_round_by_rule":stops,"matched_settings_versus_MOST":matched_table,
            "support_history_equality_by_knot_law":structural_equality,
            "archive_checks":archive_counts,"ancestry_of_made_common_witness_routes":ancestry,
            "examples":examples,"referee":reconcile_referee(args.referee,receipts)}
    if args.first is not None and args.output==ART/"analysis/reach_comparison.json":
        raise ValueError("A timing prefix needs a separate output file.")
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(f"{len(receipts)} histories, {archive_counts['anonymized_archive_rows_with_distinct_compatible_first_parts']} historical rows, referee {result['referee']['state']}")


if __name__=="__main__":
    main()

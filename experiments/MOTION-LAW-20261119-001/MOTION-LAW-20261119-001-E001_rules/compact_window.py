"""Dominance-reduced, exhaustive compact-translation search on a homogeneous path."""
from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from radius_boundary import bounded_motion_search, build, closure, local_word, next_enabled, overwrite_code
from rule_census import members, reverse


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "compact_window.json"
RADIUS = 4
MAX_EXPANDED_LABELS = 2_000_000
MAX_LABELS_PER_SEED = 100_000
MAX_CACHE_ENTRIES = 262_144


@dataclass
class History:
    state: int
    fire_words: int
    depth: int
    before: object = None
    fire: int | None = None
    dominated: bool = False


def undecorated(support):
    left = (support & -support).bit_length()-1
    return support>>left,left


def explorer(horn):
    _,wordbit,clauses,_,_ = horn
    viable = {word:closure(clauses,word) for word in set(wordbit) if word}

    @lru_cache(maxsize=MAX_CACHE_ENTRIES)
    def extend(current,mark):
        if current & mark:
            return current
        forced = viable[mark]
        return None if forced is None else closure(clauses,current|forced)

    @lru_cache(maxsize=MAX_CACHE_ENTRIES)
    def relative_actions(pattern):
        actions = []
        for i in range(-1,pattern.bit_length()+1):
            reading = wordbit[local_word(pattern,i,RADIUS)]
            if reading and viable[reading] is not None:
                actions.append((i,reading))
        return tuple(actions)

    return extend,relative_actions


def explore_seed(seed,event_cap,expand_cap,extend,relative_actions):
    origin = event_cap+1
    initial = seed<<origin
    entrance = History(initial,0,0)
    breadth = deque([entrance])
    antichains = {initial:[entrance]}
    tally = Counter({"labels_accepted":1})
    while breadth:
        current = breadth.popleft()
        if current.dominated:
            tally["queued_dominated_labels_skipped"] += 1
            continue
        pattern,position = undecorated(current.state)
        if pattern==seed and position!=origin:
            return "translation",tally,current
        if tally["expanded"]>=expand_cap:
            return "global_expansion_cap",tally,None
        tally["expanded"] += 1
        if current.depth==event_cap:
            continue
        level = current.depth+1
        for relative,reading in relative_actions(pattern):
            wordset = extend(current.fire_words,reading)
            if wordset is None:
                tally["inconsistent_extensions"] += 1
                continue
            fire = position+relative
            assert fire>=0
            child_state = current.state^(1<<fire)
            active = antichains.get(child_state, ())
            if any(existing.depth<=level and existing.fire_words & wordset == existing.fire_words
                   for existing in active):
                tally["subsumed_extensions"] += 1
                continue
            if tally["labels_accepted"]>=MAX_LABELS_PER_SEED:
                return "per_seed_label_cap",tally,None
            new = History(child_state,wordset,level,current,fire)
            remaining = []
            for existing in active:
                if level<=existing.depth and existing.fire_words & wordset == wordset:
                    existing.dominated = True
                    tally["older_supersets_dominated"] += 1
                else:
                    remaining.append(existing)
            antichains[child_state] = [*remaining,new]
            breadth.append(new)
            tally["labels_accepted"] += 1
    tally["different_absolute_supports"] = len(antichains)
    return "complete",tally,None


def replay(seed,terminal,event_cap,horn):
    permitted,wordbit,clauses,_,_ = horn
    origin = event_cap+1
    initial = seed<<origin
    rule = terminal.fire_words
    turns = []
    trace = terminal
    while trace.before is not None:
        turns.append(trace.fire)
        trace = trace.before
    assert trace.state==initial
    state = initial
    phases = []
    for fired in reversed(turns):
        eligible = next_enabled(state,rule,wordbit,RADIUS)
        assert fired in eligible
        after = state^(1<<fired)
        phases.append({"before":[i-origin for i in members(state)],"fired":fired-origin,
                       "enabled":[i-origin for i in eligible],"after":[i-origin for i in members(after)]})
        state = after
    shape,position = undecorated(state)
    shift = position-origin
    assert shape==seed and shift and state==terminal.state
    return {"initial_support":list(members(seed)),"translation":shift,"phases":phases,
            "event_count":len(phases),"each_phase_has_unique_fire":all(len(p["enabled"])==1 for p in phases),
            "repeatable_schedule_is_weakly_fair":True,
            "all_fair_schedules_translate":"not tested" if any(len(p["enabled"])>1 for p in phases) else True,
            "rule":overwrite_code(RADIUS,rule,permitted)}


def window(span,event,horn):
    extend,actions = explorer(horn)
    total = Counter()
    covered = Counter()
    tested = Counter()
    verdict = "completed"
    witness = None
    last = None
    for seed in range(1,1<<span,2):
        width = seed.bit_length()
        other = reverse(seed,width)
        if other<seed:
            continue
        tested[width] += 1
        status,history,terminal = explore_seed(seed,event,MAX_EXPANDED_LABELS-total["expanded"],extend,actions)
        total.update(history)
        last = {"seed":list(members(seed)),"status":status}
        if terminal is not None:
            witness = replay(seed,terminal,event,horn)
            verdict = "translation"
            break
        if status!="complete":
            verdict = status
            break
        covered[width] += 1 if other==seed else 2

    return {"radius":RADIUS,"initial_span_cap":span,"event_cap":event,"candidate_starts":1<<(span-1),
            "globally_max_expanded_labels":MAX_EXPANDED_LABELS,"max_cumulative_labels_per_seed":MAX_LABELS_PER_SEED,
            "cache_size_bound":MAX_CACHE_ENTRIES,"verdict":verdict,"last_representative":last,
            "directly_tested_reflection_representatives_by_span":dict(tested),
            "completed_negative_starts_including_reflections_by_span":dict(covered),
            "completed_negative_starts_including_reflections":sum(covered.values()),"totals":dict(total),
            "witness":witness}


def main():
    permitted,wordbit,clauses = build(RADIUS)
    horn = (permitted,wordbit,clauses,None,None)
    smaller = window(8,8,horn)
    previous = bounded_motion_search(RADIUS,horn,8,8,250_000)
    assert previous["entire_window_completed"] and previous["starts_exhausted_without_a_translation"]==128
    assert smaller["verdict"]=="completed" and smaller["completed_negative_starts_including_reflections"]==128
    assert previous["translated_repeatable_witness"] is None and smaller["witness"] is None
    print("128-start agreement",smaller["totals"],flush=True)
    enlarged = window(12,16,horn)
    record = {"source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
              "comparison_window_new":smaller,"comparison_window_previous":previous,"expanded_window":enlarged,
              "coverage_note":"Reflected initial supports and displacements are transported; absolute support is retained within each search.",
              "subsumption_note":"An earlier or equally short route with a subset of forced firing words can undergo every legal continuation of a more constrained route at the same support."}
    ARTIFACT.write_text(json.dumps(record,indent=2)+"\n")
    print(enlarged,flush=True)


if __name__=="__main__":
    main()

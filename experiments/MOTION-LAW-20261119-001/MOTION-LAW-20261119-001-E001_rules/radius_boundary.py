"""Exact Horn reduction for reflected conservative single-slot updates."""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from rule_census import explicit_local, members, reflection_table, reverse


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "radius_boundary.json"


def build(radius):
    width = 2*radius+1
    full = (1 << width)-1
    reps, table = reflection_table(radius)
    permitted = [w for w in reps if (w>>(radius-1)&1)!=(w>>(radius+1)&1)]
    names = {w:i for i,w in enumerate(permitted)}
    wordbit = [1<<names[reps[table[w]]] if reps[table[w]] in names else 0 for w in range(1 << width)]
    clauses = set()
    for distance in range(1,radius+1):
        for joint in range(1 << (width+distance)):
            first,second = joint & full, joint>>distance & full
            a,b = wordbit[first],wordbit[second]
            if not a or not b:
                continue
            antecedents = a|b
            for consequence in (wordbit[first^(1<<(radius+distance))], wordbit[second^(1<<(radius-distance))]):
                if not antecedents & consequence:
                    clauses.add((antecedents,consequence))
    return permitted,wordbit,tuple(sorted(clauses))


def closure(clauses, enabled):
    while True:
        forced = enabled
        for p,c in clauses:
            if p & enabled == p:
                if not c:
                    return None
                forced |= c
        if forced == enabled:
            return enabled
        enabled = forced


def assignment_holds(clauses,on):
    return all(p & on != p or c & on for p,c in clauses)


def normalize(clauses):
    on = off = 0
    while True:
        remaining = set()
        next_on,next_off = on,off
        for p,c in clauses:
            if p & off or c & on:
                continue
            p &= ~on
            c &= ~off
            if not p:
                if not c:
                    return None
                next_on |= c
            elif not c and p.bit_count()==1:
                next_off |= p
            else:
                remaining.add((p,c))
        if next_on & next_off:
            return None
        if next_on==on and next_off==off:
            return on,off,tuple(sorted(remaining))
        on,off = next_on,next_off


def connected_parts(clauses):
    components = []
    for p,c in clauses:
        link = p|c
        others = []
        for comp in components:
            if comp & link:
                link |= comp
            else:
                others.append(comp)
        components = [*others,link]
    return components


class Cutoff(Exception):
    pass


def count_models(clauses,size,cap):
    visited = 0
    horizon = (1<<size)-1

    @lru_cache(None)
    def count(universe,remaining):
        nonlocal visited
        if visited==cap:
            raise Cutoff
        visited += 1
        reduced = normalize(remaining)
        if reduced is None:
            return 0
        on,off,active = reduced
        universe &= ~(on|off)
        components = connected_parts(active)
        free = universe ^ sum(components)
        assert free & universe == free
        if not components:
            return 1<<free.bit_count()
        if len(components)>1:
            answer = 1<<free.bit_count()
            for region in components:
                part = tuple((p,c) for p,c in active if (p|c)&region)
                answer *= count(region,part)
            return answer
        incident = Counter(v for p,c in active for v in members(p|c))
        pivot = 1 << max(incident,key=lambda v: (incident[v],-v))
        branch = sum(count(components[0],tuple(sorted([*active,unit]))) for unit in ((0,pivot),(pivot,0)))
        return branch << free.bit_count()

    try:
        return count(horizon,clauses),visited
    except Cutoff:
        return None,visited


def collect_models(clauses,size,expected):
    models = []
    universe = (1<<size)-1

    def visit(remaining,known_on,live):
        reduced = normalize(live)
        if reduced is None:
            return
        on,off,active = reduced
        remaining &= ~(on|off)
        known_on |= on
        if not remaining:
            models.append(known_on)
            return
        pivot = remaining & -remaining
        for unit in ((0,pivot),(pivot,0)):
            visit(remaining,known_on,(*active,unit))

    visit(universe,0,clauses)
    assert len(models)==expected and len(set(models))==expected
    assert all(assignment_holds(clauses,code) for code in models)
    return sorted(models)


def word_string(word,radius):
    return "".join(str(word>>i&1) for i in range(2*radius+1))


def overwrite_code(radius,row,permitted):
    reps,lookup = reflection_table(radius)
    classes = {word:i for i,word in enumerate(reps)}
    identity = sum((word>>radius&1)<<j for j,word in enumerate(reps))
    overwritten = identity ^ sum(1<<classes[permitted[j]] for j in members(row))
    checked, examples = explicit_local(radius,lookup,overwritten)
    assert checked["enabled_diamond"] and checked["quiet_zero"]
    local = (1 << (2*radius+1))-1
    reversible = all(((overwritten >> lookup[x]) ^ (overwritten >> lookup[x ^ (1<<radius)])) & 1 for x in range(local+1))
    return {"firing_mask":hex(row), "overwrite_truth_code":hex(overwritten),
            "trigger_representatives_left_to_right":[word_string(permitted[j],radius) for j in members(row)],
            "literal_property_check":{**checked,"each_site_is_reversible":reversible},
            "literal_failure_witnesses":examples}


def creation_arrows(radius,row,wordbit,permitted):
    width = 2*radius+1
    cut = (1<<width)-1
    witnesses = {}
    for gap in range(1,radius+1):
        for whole in range(1<<(width+gap)):
            left,right = whole & cut,whole>>gap & cut
            for a,b,d in ((left,right,gap),(right,left,-gap)):
                if not wordbit[a] & row:
                    continue
                changed = b ^ (1<<(radius-d))
                if not wordbit[b]&row and wordbit[changed]&row:
                    key = (wordbit[a],wordbit[changed],d)
                    witnesses.setdefault(key,(whole,a,b,changed))
    return [{"fires":word_string(permitted[p.bit_length()-1],radius),
             "creates":word_string(permitted[c.bit_length()-1],radius),
             "relative_reading_offset":d,
             "joint_witness_left_to_right":"".join(str(whole>>i & 1) for i in range(width+abs(d))),
             "first_word":word_string(a,radius),"newly_enabled_word_before":word_string(b,radius),
             "newly_enabled_word_after":word_string(changed,radius)}
            for (p,c,d),(whole,a,b,changed) in sorted(witnesses.items())]


def reversible_guard(radius):
    permitted,wordbit,_ = build(radius)
    width = 2*radius+1
    tested = 0
    for raw in range(1<<width):
        if raw>>radius & 1 or not wordbit[raw]:
            continue
        tested += 1
        normal = {i:raw>>(radius+i) & 1 for i in range(-radius,radius+1) if i}
        mirror = {-i:v for i,v in normal.items()}
        mismatches = []
        for naming_left,left in (("direct",normal),("reflected",mirror)):
            for naming_right,right in (("direct",normal),("reflected",mirror)):
                for gap in range(1,radius+1):
                    mismatch = next((i for i in sorted(left) if i-gap in right and left[i]!=right[i-gap]),None)
                    if mismatch is not None:
                        mismatches.append([naming_left,naming_right,gap,mismatch])
        if len(mismatches)!=4*radius:
            continue
        firing = wordbit[raw] | wordbit[raw ^ (1<<radius)]
        receipt = overwrite_code(radius,firing,permitted)
        assert receipt["literal_property_check"]["each_site_is_reversible"]
        assert receipt["literal_property_check"]["commutes"]
        assert not receipt["literal_property_check"]["idempotent"]
        text = word_string(raw,radius)
        pattern = text[:radius]+"*"+text[radius+1:]
        return {"radius":radius,"outer_guard":pattern,"reflected_outer_guard":pattern[::-1],
                "overlap_mismatches":mismatches, "literal_rule":receipt, "raw_guards_checked":tested}
    return None


def local_word(state,slot,radius):
    lo = slot-radius
    shifted = state>>lo if lo>=0 else state<<-lo
    return shifted & ((1<<(2*radius+1))-1)


def next_enabled(state,row,wordbit,radius):
    return [slot for slot in range(-1,state.bit_length()+1)
            if wordbit[local_word(state,slot,radius)] & row]


def minimal_translation_search(radius,inputs,span_bound,run_bound,visit_cap):
    permitted,wordbit,clauses,_,_ = inputs
    possible = [closure(clauses,1<<i) for i in range(len(permitted))]
    restricted = [x is not None for x in possible]
    visited = starts = 0
    early = None
    completely_forced = None

    @lru_cache(None)
    def extend(row, marks):
        use = possible[marks.bit_length()-1]
        if use is None:
            return None
        return closure(clauses,row|use)

    def scan(source,state,outstanding,enabled,trail):
        nonlocal visited,early,completely_forced
        if visited==visit_cap:
            raise Cutoff
        visited += 1
        if not outstanding:
            assert state==source<<1 and assignment_holds(clauses,enabled)
            phases = next_enabled(source,enabled,wordbit,radius)
            state = source
            choices = []
            for selected in trail:
                at = next_enabled(state,enabled,wordbit,radius)
                assert selected in at
                choices.append(at)
                state ^= 1<<selected
            assert phases==choices[0]
            receipt = {"initial_support":list(members(source)),
                       "phase_fires":list(trail),"enabled_choices_per_phase":choices,
                       "literal_rule":overwrite_code(radius,enabled,permitted)}
            if early is None:
                early = receipt
            if all(len(x)==1 for x in choices):
                completely_forced = receipt
            return
        for slot in members(outstanding):
            flag = wordbit[local_word(state,slot,radius)]
            if not flag or not restricted[flag.bit_length()-1]:
                continue
            upgraded = extend(enabled,flag)
            if upgraded is not None:
                scan(source,state^(1<<slot),outstanding^(1<<slot),upgraded,[*trail,slot])
                if completely_forced is not None:
                    return

    try:
        for start in range(1,1<<span_bound,2):
            difference = start^(start<<1)
            if difference.bit_count()>2*run_bound:
                continue
            starts += 1
            scan(start,start,difference,0,[])
            if completely_forced is not None:
                break
    except Cutoff:
        pass
    return {"radius":radius,"initial_span_cap":span_bound,"initial_occupied_run_cap":run_bound,
            "visits":visited,"visit_cap":visit_cap,"normalized_starts_tested":starts,
            "exhausted_window":visited<visit_cap and completely_forced is None,
            "admissible_minimum_length_route":early,"unique_fire_route":completely_forced}


def bounded_motion_search(radius,inputs,span_bound,event_bound,visit_cap):
    permitted,wordbit,clauses,_,_ = inputs
    possible = {1<<i:closure(clauses,1<<i) for i in range(len(permitted))}
    checked = 0
    starts = 0
    intact = None
    visits = 0
    center = event_bound + 1

    @lru_cache(None)
    def set_guard(enabled,word):
        taken = possible.get(word)
        return None if taken is None else closure(clauses,enabled|taken)

    def scan(seed,state,enabled,history,appearances):
        nonlocal visits,intact
        if visits==visit_cap:
            raise Cutoff
        visits += 1
        start = next(members(state))
        if state >> start == seed and start!=center:
            check = seed << center
            branches = []
            for at in history:
                choices = next_enabled(check,enabled,wordbit,radius)
                assert at in choices
                branches.append([v-center for v in choices])
                check ^= 1<<at
            assert check==state
            intact = {"initial_support":list(members(seed)), "translation":start-center,
                      "events":[v-center for v in history],"total_options_at_each_phase":branches,
                      "literal_rule":overwrite_code(radius,enabled,permitted)}
            return
        if len(history)==event_bound:
            return
        for site in range(start-1,state.bit_length()+1):
            word = wordbit[local_word(state,site,radius)]
            after = state^(1<<site)
            if after in appearances:
                continue
            action = set_guard(enabled,word)
            if action is not None:
                scan(seed,after,action,[*history,site],appearances|{after})
                if intact:
                    return

    try:
        for seed in range(1,1<<span_bound,2):
            starts += 1
            initial = seed << center
            scan(seed,initial,0,[],{initial})
            if intact:
                break
            checked += 1
    except Cutoff:
        pass
    return {"radius":radius,"initial_span_cap":span_bound,"event_cap":event_bound,"visit_cap":visit_cap,
            "visits":visits,"starts_entered":starts,"starts_exhausted_without_a_translation":checked,
            "entire_window_completed":checked==(1<<(span_bound-1)),
            "translated_repeatable_witness":intact}


def study(radius,count_cap):
    permitted,wordbit,clauses = build(radius)
    initials = [closure(clauses,1<<j) for j in range(len(permitted))]
    nontrivial = sorted({row for row in initials if row is not None},key=lambda row: (row.bit_count(),row))
    amount,nodes = count_models(clauses,len(permitted),count_cap)
    models = collect_models(clauses,len(permitted),amount) if amount is not None and amount <= 2048 else None
    witness = overwrite_code(radius,nontrivial[0],permitted) if nontrivial else None
    by_shape = Counter((p.bit_count(),bool(c)) for p,c in clauses)
    result = {"radius":radius,"allowed_reflection_classes":len(permitted),
              "horn_clause_counts":[{"antecedents":n,"positive_consequence":c,"count":k} for (n,c),k in sorted(by_shape.items())],
              "eligible_single_trigger_tests":len(initials),"triggers_with_satisfiable_least_closure":sum(x is not None for x in initials),
              "distinct_nonempty_least_closures":len(nontrivial),
              "least_closure_size_histogram":dict(Counter(x.bit_count() for x in nontrivial)),
              "smallest_firing_rule":witness,"model_count":amount,"model_count_nodes":nodes,"model_count_cap":count_cap,
              "all_model_masks_hex":None if models is None else [hex(x) for x in models]}
    if models is not None:
        indices = [j for j,row in enumerate(initials) if row is not None]
        exact = []
        for option in range(1<<len(indices)):
            row = sum(1<<indices[j] for j in members(option))
            if assignment_holds(clauses,row):
                exact.append(row)
        assert sorted(exact)==models
        result["literal_subset_count_check"] = {"possible_trigger_bits":len(indices),"all_subsets_tested":1<<len(indices)}
    print(radius,result["model_count"],result["triggers_with_satisfiable_least_closure"],witness,flush=True)
    return result,(permitted,wordbit,clauses,models,nontrivial)


def main():
    rows = []
    causal = []
    mobility = None
    broader = None
    capped_stress = None
    for radius in (1,2,3,4):
        result,horn = study(radius,250000)
        rows.append(result)
        if radius==3:
            permitted,wordbit,_,models,_ = horn
            result["literal_checks_on_every_model"] = [overwrite_code(3,row,permitted) for row in models]
            for row,checked in zip(models,result["literal_checks_on_every_model"]):
                arrows = creation_arrows(3,row,wordbit,permitted)
                assert bool(arrows)==(not checked["literal_property_check"]["commutes"])
                assert not {a["fires"] for a in arrows} & {a["creates"] for a in arrows}
                assert all(abs(a["relative_reading_offset"])==3 for a in arrows)
                causal.append({"rule_mask":hex(row),"arrows":arrows,"finite_seed_reach_bound":6 if arrows else 3})
        if radius==4:
            mobility = minimal_translation_search(4,horn,10,3,250000)
            broader = bounded_motion_search(4,horn,8,8,250000)
            capped_stress = bounded_motion_search(4,horn,12,16,250000)
    reversible = reversible_guard(4)
    assert reversible is not None and reversible_guard(3) is None
    record = {"program_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),"radii":rows,
              "radius_three_causal_creation":causal,"explicit_reversible_guard":reversible,
              "radius_four_minimal_compact_motion_search":mobility,"radius_four_bounded_compact_motion_search":broader,
              "radius_four_motion_stress":capped_stress}
    OUTPUT.write_text(json.dumps(record,indent=2)+"\n")


if __name__=="__main__":
    main()

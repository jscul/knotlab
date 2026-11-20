"""Exact reflected single-site overwrite-map and finite enabled-history census."""
from collections import Counter, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "rule_census.json"
PATH_SIZES = range(1, 11)
RING_SIZES = range(3, 9)
PROPERTIES = ("quiet_zero", "idempotent", "commutes", "enabled_diamond")


def reverse(word, width):
    result = 0
    for _ in range(width):
        result = (result << 1) | (word & 1)
        word >>= 1
    return result


def reflection_table(radius):
    width = 2*radius+1
    classes = [min(w, reverse(w,width)) for w in range(1 << width)]
    reps = sorted(set(classes))
    index = {word:i for i,word in enumerate(reps)}
    return reps, tuple(index[w] for w in classes)


def bitplanes(size):
    count = 1 << size
    planes = []
    for j in range(size):
        stride = 1 << j
        band = ((1 << stride)-1) << stride
        filled = stride*2
        while filled < count:
            band |= band << filled
            filled *= 2
        planes.append(band)
    return (1 << count)-1, tuple(planes)


def local_predicates(radius):
    reps, lookup = reflection_table(radius)
    full, rulebit = bitplanes(len(reps))
    width = 2*radius+1
    window = (1 << width)-1

    def produces(column, value):
        return rulebit[column] if value else full ^ rulebit[column]

    idem = full
    for before in range(1 << width):
        held = before >> radius & 1
        old = lookup[before]
        changed = lookup[before ^ (1 << radius)]
        idem &= full ^ (produces(old, 1-held) & produces(changed,held))

    separate = {}
    commuting, diamond = full,full
    for step in range(1,radius+1):
        here, coenabled = full,full
        for holder_word in range(1 << (width+step)):
            a,b = holder_word & window, holder_word >> step & window
            x,y = a >> radius & 1,b >> radius & 1
            first,second = lookup[a],lookup[b]
            a_changed = lookup[a ^ (1 << (radius+step))]
            b_changed = lookup[b ^ (1 << (radius-step))]
            disagree_first = rulebit[first] ^ rulebit[a_changed]
            disagree_second = rulebit[second] ^ rulebit[b_changed]
            first_changes = produces(first,1-x)
            second_changes = produces(second,1-y)
            here &= full ^ ((second_changes & disagree_first) | (first_changes & disagree_second))
            coenabled &= full ^ (first_changes & second_changes & (disagree_first | disagree_second))
        commuting &= here
        diamond &= coenabled
        separate[step] = {"joint_binary_inputs": 1 << (width+step), "commutes": here.bit_count(),
                          "enabled_diamond": coenabled.bit_count()}

    spans = {}
    for smaller in range(radius+1):
        retained = ((1 << (2*smaller+1))-1) << (radius-smaller)
        agrees = full
        for word in range(1 << width):
            agrees &= full ^ (rulebit[lookup[word]] ^ rulebit[lookup[word & retained]])
        spans[smaller] = agrees
    flags = {"quiet_zero": full ^ rulebit[0], "idempotent": idem,
             "commutes": commuting, "enabled_diamond": diamond}
    return reps, lookup, full, flags, separate, spans


def has_member(group, rule):
    return bool(group >> rule & 1)


def classify_local(radius):
    reps, lookup, full, flags, separate, spans = local_predicates(radius)
    properties = {name: token.bit_count() for name,token in flags.items()}
    quiet = flags["quiet_zero"]
    by_truth = []
    for row in product((False,True), repeat=len(flags)):
        valid = full
        for prop,value in zip(flags,row):
            valid &= flags[prop] if value else full ^ flags[prop]
        if valid:
            by_truth.append({"properties": dict(zip(flags,row)), "count": valid.bit_count()})

    def summarize(flag):
        count = flag.bit_count()
        result = {"count":count}
        if count <= 128:
            result["rules"] = list(members(flag))
        return result

    strong = flags["commutes"]
    idempotent = flags["idempotent"]
    span_count = {}
    prior = 0
    for r,span in spans.items():
        exact = span ^ prior
        span_count[r] = {"all":exact.bit_count(), "quiet_zero":(exact & quiet).bit_count(),
                         "commuting":(exact & strong).bit_count(),
                         "quiet_zero_commuting":(exact & quiet & strong).bit_count(),
                         "quiet_zero_enabled_diamond":(exact & quiet & flags["enabled_diamond"]).bit_count()}
        prior = span
    result = {"radius":radius, "reflection_word_representatives":reps, "rule_count":1 << len(reps),
              "counts_over_all_rules":properties,
              "counts_conditional_on_quiet_zero":{k:(v&quiet).bit_count() for k,v in flags.items()},
              "minimum_effective_radius":span_count, "pair_displacements":separate,
              "joint_property_histogram":by_truth,
              "commuting":summarize(strong), "quiet_zero_commuting":summarize(quiet & strong),
              "quiet_zero_commuting_idempotent":summarize(quiet & strong & idempotent),
              "quiet_zero_enabled_diamond":summarize(quiet & flags["enabled_diamond"])}
    _,rulebit = bitplanes(len(reps))
    width = 2*radius+1
    window = (1<<width)-1
    conserves, complement = full,full
    for word in range(1 << width):
        left,right = word>>(radius-1)&1,word>>(radius+1)&1
        output = rulebit[lookup[word]]
        if left==right:
            owned = word>>radius&1
            conserves &= output if owned else full ^ output
        complement &= output ^ rulebit[lookup[word ^ window]]
    identity = sum((word >> radius & 1) << j for j,word in enumerate(reps))
    eligible_slots = [j for j,word in enumerate(reps)
                      if (word>>(radius-1)&1)!=(word>>(radius+1)&1)]
    literal_conservative = {identity ^ sum(1 << eligible_slots[j] for j in members(subset))
                            for subset in range(1 << len(eligible_slots))}
    assert literal_conservative == set(members(conserves))
    literal_persistent = {rule for rule in literal_conservative
                          if explicit_local(radius,lookup,rule)[0]["enabled_diamond"]}
    assert literal_persistent == set(members(conserves & flags["enabled_diamond"]))
    result["conserves_adjacent_disagreements_for_reflected_rules"] = {
        "literal_conservative_compositions_checked":len(literal_conservative),
        "all_conservative":summarize(conserves),
        "persistent_conservative":summarize(conserves & flags["enabled_diamond"]),
        "persistent_conservative_and_complement_equivariant":summarize(conserves & flags["enabled_diamond"] & complement),
        "strongly_commuting_conservative":summarize(conserves & strong),
    }
    assert sum(row["count"] for row in by_truth) == 1 << len(reps)
    assert not strong & ~flags["enabled_diamond"]
    return result, lookup, flags


def members(mask):
    while mask:
        first = mask & -mask
        yield first.bit_length()-1
        mask ^= first


def explicit_local(radius, lookup, rule):
    """Recalculate from actual compositions on literal binary windows."""
    width = 2*radius+1
    cut = (1 << width)-1
    examples = {}

    def put(state, first):
        point = first + radius
        word = state >> first & cut
        value = rule >> lookup[word] & 1
        return (state & ~(1 << point)) | (value << point)

    for x in range(1 << width):
        y = put(x,0)
        z = put(y,0)
        if y != z:
            examples.setdefault("idempotent", [x,y,z])
    for d in range(1,radius+2):
        for source in range(1 << (width+d)):
            first,second = put(source,0),put(source,d)
            ab,ba = put(first,d),put(second,0)
            if ab != ba:
                assert d <= radius
                witness = {"displacement":d, "source":source, "first_only":first, "second_only":second,
                           "first_then_second":ab, "second_then_first":ba, "width":width+d}
                examples.setdefault("commutes", witness)
                if first != source and second != source:
                    examples.setdefault("enabled_diamond",witness)
    values = {k: k not in examples for k in PROPERTIES[1:]}
    return {"quiet_zero":put(0,0)==0, **values},examples


def encode_rule(radius, lookup, rule_function):
    result = 0
    for word in range(1 << (2*radius+1)):
        row = tuple(word >> i & 1 for i in range(2*radius+1))
        if rule_function(row[radius],row[:radius]+row[radius+1:]):
            result |= 1 << lookup[word]
    return result


def named_rules(radius,lookup):
    sources = {"identity":lambda own,n:own, "zero":lambda own,n:0, "one":lambda own,n:1,
               "toggle":lambda own,n:1-own, "spread_one":lambda own,n:own or any(n),
               "fill_gaps":lambda own,n:own or all(n), "clear_isolated":lambda own,n:own and any(n),
               "fill_outer_gap":lambda own,n:own or (n[0] and n[-1]),
               "majority":lambda own,n: own+sum(n)>radius}
    return {k:encode_rule(radius,lookup,f) for k,f in sources.items()}


def local_control(radius,lookup,flags,named):
    labels = {}
    population = range(64) if radius == 1 else sorted(set(named.values()) | {1,1537,32767,456789,970213})
    for rule in population:
        properties, witnesses = explicit_local(radius,lookup,rule)
        assert properties == {name:has_member(group,rule) for name,group in flags.items()}
        labels[rule] = witnesses
    return {"literal_composition_rules_checked":len(labels),
            "named_examples":{name:{"rule":code, "properties":{n:has_member(b,code) for n,b in flags.items()},
                                    "local_failure_witnesses":labels[code]} for name,code in named.items()}}


def input_columns(n, wrap, lookup):
    """All zero-padded path or circular nearest-neighbour words, before applying a rule."""
    before = tuple((i-1)%n if wrap else i-1 for i in range(n))
    after = tuple((i+1)%n if wrap else i+1 for i in range(n))
    return [tuple(lookup[(state >> a & 1 if a>=0 else 0) | (state >> i & 1) << 1 | (state >> b & 1) << 2]
                  for i,(a,b) in enumerate(zip(before,after))) for state in range(1 << n)]


def enabled_graph(columns, rule):
    return [tuple(state ^ (1 << i) for i,value in enumerate(row) if (rule >> value ^ state >> i) & 1)
            for state,row in enumerate(columns)]


def strong_components(graph):
    count = len(graph)
    inverse = [[] for _ in graph]
    for x,outgoing in enumerate(graph):
        for y in outgoing:
            inverse[y].append(x)
    seen = bytearray(count)
    finished = []
    for start in range(count):
        if seen[start]:
            continue
        walk = [start]
        while walk:
            u = walk.pop()
            if u < 0:
                finished.append(~u)
            elif not seen[u]:
                seen[u] = 1
                walk.append(~u)
                walk.extend(v for v in graph[u] if not seen[v])
    labels = [-1]*count
    components = []
    for start in reversed(finished):
        if labels[start] >= 0:
            continue
        pending = [start]
        number = len(components)
        labels[start] = number
        for u in pending:
            for v in inverse[u]:
                if labels[v] < 0:
                    labels[v] = number
                    pending.append(v)
        components.append(pending)
    return labels,components


def codebook(n, graph):
    labels,components = strong_components(graph)
    reachable_terminal = [0]*len(components)
    reachable_sink = [0]*len(components)
    reachable_cycle = [False]*len(components)
    reachable_fair_cycle = [False]*len(components)
    cyclic_count = 0
    fair_count = 0
    for c in reversed(range(len(components))):
        held_here = components[c]
        successors = {labels[y] for x in held_here for y in graph[x]} - {c}
        assert all(dest > c for dest in successors)
        own_cycle = len(held_here)>1
        if own_cycle:
            cyclic_count += 1
            persistent = (1<<n)-1
            internal = 0
            for state in held_here:
                firing = 0
                for after in graph[state]:
                    changed = state ^ after
                    firing |= changed
                    if labels[after] == c:
                        internal |= changed
                persistent &= firing
            own_fair_cycle = not persistent & ~internal
            fair_count += own_fair_cycle
        else:
            own_fair_cycle = False
        reachable_cycle[c] = own_cycle
        reachable_fair_cycle[c] = own_fair_cycle
        if not successors:
            reachable_sink[c] = 1 << c
            if len(held_here)==1:
                reachable_terminal[c] = 1 << held_here[0]
        for d in successors:
            reachable_terminal[c] |= reachable_terminal[d]
            reachable_sink[c] |= reachable_sink[d]
            reachable_cycle[c] |= reachable_cycle[d]
            reachable_fair_cycle[c] |= reachable_fair_cycle[d]

    terminals = Counter(min(2,reachable_terminal[c].bit_count()) for c in labels)
    multiple_sinks = sum(reachable_sink[c].bit_count()>1 for c in labels)
    result = {"states":len(graph), "literal_terminal_states":sum(not row for row in graph),
              "strong_components":len(components),"cyclic_components":cyclic_count,
              "weakly_fair_cyclic_components":fair_count,
              "states_reaching_zero_terminals":terminals[0], "states_reaching_one_terminal":terminals[1],
              "states_reaching_multiple_terminals":terminals[2], "states_reaching_multiple_sink_components":multiple_sinks,
              "states_admitting_an_infinite_history":sum(reachable_cycle[c] for c in labels),
              "states_admitting_a_weakly_fair_infinite_history":sum(reachable_fair_cycle[c] for c in labels)}
    return result,labels,reachable_terminal,reachable_sink


def trace_to(graph,start,target):
    previous = {start:None}
    pending = [start]
    for x in pending:
        if x == target:
            reversed_steps = [x]
            while previous[x] is not None:
                x = previous[x]
                reversed_steps.append(x)
            return list(reversed(reversed_steps))
        for y in graph[x]:
            if y not in previous:
                previous[y] = x
                pending.append(y)
    raise AssertionError("listed target was not reachable")


def history_census(lookup,flags):
    measurements = {rule:{} for rule in range(64)}
    smallest = {}
    boards = [(False,n) for n in PATH_SIZES]+[(True,n) for n in RING_SIZES]
    for wrap,n in boards:
        tag = f"{'ring' if wrap else 'path'}-{n}"
        columns = input_columns(n,wrap,lookup)
        for rule in measurements:
            graph = enabled_graph(columns,rule)
            result,labels,terms,sinks = codebook(n,graph)
            if n <= 4:
                for source in range(len(graph)):
                    found = {source}
                    queue = [source]
                    for x in queue:
                        for y in graph[x]:
                            if y not in found:
                                found.add(y)
                                queue.append(y)
                    assert terms[labels[source]] == sum(1 << x for x in found if not graph[x])
            measurements[rule][tag] = result
            if has_member(flags["enabled_diamond"],rule):
                assert result["states_reaching_multiple_sink_components"] == 0
            if has_member(flags["commutes"] & flags["idempotent"],rule):
                assert result["states_reaching_one_terminal"] == len(graph) and not result["cyclic_components"]
            if result["states_reaching_multiple_terminals"] and rule not in smallest:
                source = next(x for x,c in enumerate(labels) if terms[c].bit_count()>1)
                a,b,*_ = list(members(terms[labels[source]]))
                smallest[rule] = {"board":tag,"width":n,"initial":source,"terminal_histories":
                                  [trace_to(graph,source,a),trace_to(graph,source,b)]}
    normalized = {
        "terminal_confluent_on_all_boards": "states_reaching_multiple_terminals",
        "full_joinability_on_all_boards": "states_reaching_multiple_sink_components",
        "all_initial_states_weakly_normalize_on_all_boards": "states_reaching_zero_terminals",
        "all_initial_states_strongly_normalize_on_all_boards": "states_admitting_an_infinite_history",
        "all_initial_states_terminate_under_weak_fairness_on_all_boards": "states_admitting_a_weakly_fair_infinite_history",
    }
    history_counts = {}
    for name,key in normalized.items():
        eligible = [rule for rule,cases in measurements.items() if all(not row[key] for row in cases.values())]
        history_counts[name] = {"all":len(eligible), "quiet_zero":sum(rule%2==0 for rule in eligible), "rules":eligible}

    jointly = Counter()
    combined = {}
    for rule,cases in measurements.items():
        counts = {name:has_member(flag,rule) for name,flag in flags.items()}
        counts.update({name:all(row[key]==0 for row in cases.values()) for name,key in normalized.items()})
        jointly[tuple(counts.values())] += 1
        combined[rule] = counts

    normalize_and_join = [rule for rule,counts in combined.items()
                          if counts["all_initial_states_weakly_normalize_on_all_boards"]
                          and counts["terminal_confluent_on_all_boards"]]
    fairly_terminate_and_join = [rule for rule in normalize_and_join
                                 if combined[rule]["all_initial_states_terminate_under_weak_fairness_on_all_boards"]]
    for name,rules in (("unique_reachable_terminal_on_all_boards",normalize_and_join),
                       ("every_weakly_fair_history_same_terminal_on_all_boards",fairly_terminate_and_join)):
        history_counts[name] = {"all":len(rules), "quiet_zero":sum(rule%2==0 for rule in rules), "rules":rules}
    return {"coverage":{tag:len(input_columns(n,wrap,lookup)) for (wrap,n),tag in zip(boards,measurements[0])},
            "normalized_property_counts":history_counts,"by_rule":measurements,
            "joint_local_and_history_predicates":[{"properties":dict(zip(combined[0],row)),"count":weight}
                                                   for row,weight in jointly.items()],
            "first_two_terminal_witnesses":smallest}


def history_controls(lookup,named):
    # A positive causal trace and a failed one-pass order for the spread rule.
    width = 7
    columns = input_columns(width,False,lookup)
    infection = enabled_graph(columns,named["spread_one"])
    one_sided = [(1 << (t+1))-1 for t in range(width)]
    assert all(infection[x] == (y,) for x,y in zip(one_sided,one_sided[1:])) and not infection[one_sided[-1]]
    from_midpoint = 1 << 3
    two_neighbors = [from_midpoint | (1 << v) for v in (2,4)]
    assert infection[from_midpoint] == tuple(two_neighbors)
    full = (1 << width)-1
    traces = [[from_midpoint, *trace_to(infection,chosen,full)] for chosen in two_neighbors]

    def once(order):
        state = 1
        for i in order:
            output = named["spread_one"] >> columns[state][i] & 1
            state = (state & ~(1 << i)) | (output << i)
        return state

    forward,backward = once(range(width)),once(reversed(range(width)))
    assert (forward,backward)==(full,3)
    transient = enabled_graph(input_columns(2,False,lookup),2)
    short_clear, detour_clear, repeated = [1,0], [1,3,1,0], [1,3,2,3,1]
    for phases in (short_clear,detour_clear,repeated):
        assert all(b in transient[a] for a,b in zip(phases,phases[1:]))
    assert not transient[0] and all(trace_to(transient,start,0) for start in range(4))
    assert {((y^x).bit_length()-1) for x,y in zip(repeated,repeated[1:])} == {0,1}
    majority = enabled_graph(input_columns(3,False,lookup),named["majority"])
    collide = [[5,4,0],[5,7]]
    assert all(all(y in majority[x] for x,y in zip(path,path[1:])) and not majority[path[-1]] for path in collide)
    return {"width":width,"spread_forced_one_sided_history":one_sided,
            "spread_midpoint_histories_with_same_terminal":traces,
            "once_per_site_spread_left_to_right":forward, "once_per_site_spread_right_to_left":backward,
            "right_to_left_endpoint_still_has_enabled_sites":list(infection[backward]),
            "same_terminal_different_event_multiplicities":{"rule":2,"width":2,"terminating":[short_clear,detour_clear],
                                                            "weakly_fair_repeat":repeated},
            "majority_collision_distinct_terminals":{"rule":named["majority"],"width":3,"terminating":collide}}


def oriented_conservation():
    """All 256 oriented tables, with the disagreement and persistence filters."""
    lookup = tuple(range(8))
    identity = encode_rule(1,lookup,lambda own,neighbors:own)
    selected = []
    counts = Counter()
    nonpersistent = {}

    def symmetry(rule, mapping, flip=False):
        return sum(((rule >> mapping(w) & 1) ^ flip) << w for w in range(8))

    def reflection(rule):
        return symmetry(rule,lambda w:reverse(w,3))

    def complement(rule):
        return symmetry(rule,lambda w:w^7,flip=True)

    def spell(word):
        return "".join(str(word>>i & 1) for i in range(3))

    for rule in range(256):
        properties,witnesses = explicit_local(1,lookup,rule)
        fires = list(members(rule ^ identity))
        conserved = True
        for word in range(8):
            left,own,right = [word >> i & 1 for i in range(3)]
            out = rule >> word & 1
            conserved &= (left ^ own) + (right ^ own) == (left ^ out) + (right ^ out)
        assert conserved == all((word & 1)!=(word>>2 & 1) for word in fires)
        if not conserved:
            continue
        counts["conserves_disagreement_per_event"] += 1
        if not properties["enabled_diamond"]:
            nonpersistent[rule] = {"fires":list(map(spell,fires)), "conflict":witnesses["enabled_diamond"]}
            continue
        mirror, flips = reflection(rule)==rule, complement(rule)==rule
        counts["persistent"] += 1
        counts["persistent_and_reflected"] += mirror
        counts["persistent_and_complemented"] += flips
        counts["persistent_and_both"] += mirror and flips
        counts["persistent_and_strongly_commuting"] += properties["commutes"]
        histories = {}
        for wrap,n in ((False,7),(True,3),(True,4),(True,7),(True,8)):
            graph = enabled_graph(input_columns(n,wrap,lookup),rule)

            def disagreements(state):
                internal = sum((state>>i ^ state>>((i+1)%n)) & 1 for i in range(n if wrap else n-1))
                return internal if wrap else internal+(state&1)+(state>>(n-1)&1)

            assert all(disagreements(u)==disagreements(v) for u,edges in enumerate(graph) for v in edges)
            scored,_,_,_ = codebook(n,graph)
            assert scored["states_reaching_multiple_sink_components"]==0
            histories[f"{'ring' if wrap else 'path'}-{n}"] = scored
        selected.append({"rule":rule,"firing_words_left_own_right":list(map(spell,fires)),
                         "reflection_equivariant":mirror,"bit_complement_equivariant":flips,
                         "reflected_rule":reflection(rule),"complemented_rule":complement(rule),
                         "properties":properties,"normalized_history_controls":histories,
                         "local_failure_witnesses":witnesses})

    codes = {row["rule"] for row in selected}
    orbits = {tuple(sorted({r,reflection(r),complement(r),reflection(complement(r))})) for r in codes}
    assert set().union(*map(set,orbits))==codes
    fires_by_rule = {tuple(sorted(row["firing_words_left_own_right"])) for row in selected}
    exclusions = ({"001","011"}, {"011","110"}, {"100","001"}, {"110","100"})
    eligible_words = ("001","011","100","110")
    independent = set()
    for firing in range(16):
        firing_words = {w for j,w in enumerate(eligible_words) if firing >> j & 1}
        if all(not pair <= firing_words for pair in exclusions):
            independent.add(tuple(sorted(firing_words)))
    assert independent==fires_by_rule
    # Size-one and size-two circular words have the same two neighbors.
    assert all(not graph for row in selected for n in (1,2)
               for graph in enabled_graph(input_columns(n,True,lookup),row["rule"]))
    across = {}
    for direction,code in (("right",142),("left",212)):
        n = 7
        graph = enabled_graph(input_columns(n,True,lookup),code)
        simple_run = [1]
        for j in range(n):
            current = (j if direction=="right" else -j)%n
            step = (current+(1 if direction=="right" else -1))%n
            outset, duo, unit = (1<<current),(1<<current)|(1<<step),(1<<step)
            assert simple_run[-1]==outset and duo in graph[outset] and unit in graph[duo]
            assert len(graph[duo])>1
            simple_run.extend([duo,unit])
        assert simple_run[0]==simple_run[-1]
        across[direction] = {"rule":code,"size":n,"two_event_per_slot_selected_cyclic_trace":simple_run,
                             "compact_route_requires_a_schedule_choice":True}
    return {"oriented_tables":256,"counts":dict(counts),"selected_rules":selected,
            "adjacent_coenabled_conflict_word_pairs":[sorted(pair) for pair in exclusions],
            "oriented_compact_route_examples":across,
            "exact_conservative_nonpersistent_witnesses":nonpersistent,
            "reflection_and_complement_orbits":sorted(orbits),"short_rings_have_no_genuine_event":True}


def physical_path_control(candidates):
    prior = "EDDY-WORLD-20261119-001"
    literal = HERE.parents[2] / "artifacts" / prior / (prior+"-E001_world") / "stages.json"
    payload = literal.read_bytes()
    path = json.loads(payload)["cases"]["B"]
    ordinary = [set(row) for row in path["stages"]["1"]["stars"]]
    parents = {frozenset(row):int(j) for j,row in path["stages"]["1"]["parent_sets"].items() if len(row)==2}
    background = path["input"]["roles"]["background"]
    source_marks = set(path["input"]["roles"]["anchors"])
    quads = []
    for i in range(2,9):
        u,v,w = background[i-1:i+2]
        child = parents[frozenset((u,w))]
        support = (ordinary[u]&ordinary[v]) | (ordinary[v]&ordinary[w]) | (
                   ordinary[u]&ordinary[child]) | (ordinary[w]&ordinary[child])
        assert len(support)==4 and len(support&source_marks)==2
        quads.append(support)

    def physical(state):
        result = set()
        for i in members(state):
            result ^= quads[i]
        assert all(len(result&star)%2==0 for star in ordinary)
        return len(result&source_marks)

    source_counts = [physical(state) for state in range(1 << len(quads))]
    original_names = [tuple(sorted(q&source_marks)) for q in quads]
    assert all(len(set(a)&set(b))==1 for a,b in zip(original_names,original_names[1:]))
    columns = input_columns(len(quads),False,tuple(range(8)))
    transitions = 0
    for candidate in candidates:
        graph = enabled_graph(columns,candidate["rule"])
        for a,choices in enumerate(graph):
            for b in choices:
                assert source_counts[a]==source_counts[b]
                transitions += 1
    return {"literal_stage_sha256":sha256(payload).hexdigest(),"selected_response_supports":[sorted(q) for q in quads],
            "free_slot_states":len(source_counts),"allowed_transitions_carrying_conservation":transitions,
            "quiet_outside_closed_response_restriction":True}


def causal_depth_controls():
    controls = []
    for radius in (1,2):
        state = {0}
        stride = list(range(0,9,radius))
        for place in stride[1:]:
            assert place not in state and any(abs(old-place)<=radius for old in state)
            state.add(place)
        depth = {0:0}
        wave = {0}
        while len(depth)<9:
            layer = {i for i in range(9) if i not in depth and any(abs(j-i)<=radius for j in wave)}
            assert layer
            for k in layer:
                depth[k] = min(depth[j] for j in wave if abs(j-k)<=radius)+1
            wave = layer
        assert depth[8] == 8//radius
        controls.append({"radius":radius,"sample_path_slots":9,
                         "one_nested_causal_history_slots":stride,"minimum_depth_to_last_slot":depth[8]})
    return controls


def main():
    output = {"program_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),"local_radius":{}}
    for radius in (1,2):
        result,lookup,flags = classify_local(radius)
        named = named_rules(radius,lookup)
        result["controls"] = local_control(radius,lookup,flags,named)
        output["local_radius"][radius] = result
        if radius == 1:
            output["histories_radius_one"] = history_census(lookup,flags)
            output["history_controls"] = history_controls(lookup,named)
        print(radius,result["counts_over_all_rules"],result["counts_conditional_on_quiet_zero"],flush=True)
    output["oriented_disagreement_conservation"] = oriented_conservation()
    output["physical_path_control"] = physical_path_control(output["oriented_disagreement_conservation"]["selected_rules"])
    output["ordinary_spread_depth_controls"] = causal_depth_controls()
    print("oriented",output["oriented_disagreement_conservation"]["counts"],flush=True)
    OUTPUT.write_text(json.dumps(output,separators=(",",":")) + "\n")


if __name__ == "__main__":
    main()
